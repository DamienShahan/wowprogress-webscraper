(async () => {
  const GUILD_URLS = [
    "https://www.wowprogress.com/guild/eu/kazzak/Fragglene",
    "https://www.wowprogress.com/guild/eu/tarren-mill/this+is+fine",
    "https://www.wowprogress.com/guild/eu/drak-thul/P+L+A+C+E+H+O+L+D+E+R"
  ];

  const DELAY_MS = 1500;

  const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

  const getText = (root, selector) => {
    return root.querySelector(selector)?.innerText.trim() ?? "";
  };

  const cleanLanguage = (value) => {
    return String(value ?? "")
      .replace(/^Primary Language:\s*/i, "")
      .trim();
  };

  const cleanRaidsPerWeek = (value) => {
    return String(value ?? "")
      .replace(/^Raids per week:\s*/i, "")
      .trim();
  };

  const getGuildName = (doc) => {
    const h1Text = doc.querySelector("h1")?.innerText.trim() ?? "";
    const quotedMatch = h1Text.match(/[“"](.+?)[”"]/);

    if (quotedMatch?.[1]) {
      return quotedMatch[1].trim();
    }

    return h1Text.replace(/\s*Guild\s*$/i, "").trim();
  };

  const safeFilename = (name) => {
    return String(name || "guild")
      .trim()
      .replace(/[<>:"/\\|?*]+/g, "")
      .replace(/\s+/g, "_");
  };

  const getRecruitment = (profile, doc) => {
    const recrAll = profile.querySelector("span.recrAll");

    if (recrAll) {
      return [
        {
          class: recrAll.innerText.trim() || "all classes"
        }
      ];
    }

    return [...doc.querySelectorAll("table.recr tr")]
      .map(tr => {
        const cells = [...tr.querySelectorAll("td")];

        if (cells.length < 2) {
          return null;
        }

        const classCell = cells[0];
        const priorityCell = cells[1];

        const className = classCell.querySelector("span")?.innerText.trim() ?? "";

        const roleText = classCell.innerText
          .replace(className, "")
          .replace(/[()]/g, "")
          .trim();

        const priority =
          priorityCell.querySelector("span")?.innerText.trim()
          ?? priorityCell.innerText.trim()
          ?? "";

        if (!className || !priority) {
          return null;
        }

        return {
          class: className,
          role: roleText,
          priority
        };
      })
      .filter(Boolean);
  };

  const downloadJson = (filename, data) => {
    const json = JSON.stringify(data, null, 2);

    const blob = new Blob([json], {
      type: "application/json;charset=utf-8"
    });

    const blobUrl = URL.createObjectURL(blob);

    const a = document.createElement("a");
    a.href = blobUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();

    URL.revokeObjectURL(blobUrl);
  };

  const successfulGuilds = [];
  const failedGuilds = [];

  for (let i = 0; i < GUILD_URLS.length; i++) {
    const url = GUILD_URLS[i];

    console.log(`Fetching ${i + 1}/${GUILD_URLS.length}: ${url}`);

    try {
      const response = await fetch(url, {
        credentials: "include"
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const html = await response.text();
      const doc = new DOMParser().parseFromString(html, "text/html");
      const profile = doc.querySelector("div.guildProfile");

      if (!profile) {
        throw new Error("No div.guildProfile found");
      }

      const guildName = getGuildName(doc);

      const guildProfile = {
        url,
        guild_name: guildName,
        language: cleanLanguage(getText(profile, "div.language")),
        raids_per_week: cleanRaidsPerWeek(getText(profile, "div.raids_week")),
        description: getText(profile, "div.guildDescription"),
        recruitment: getRecruitment(profile, doc)
      };

      const filename = `${safeFilename(guildName)}.json`;

      downloadJson(filename, guildProfile);

      successfulGuilds.push({
        guild_name: guildName,
        url,
        filename
      });

      console.log(`Downloaded ${filename}`);
    } catch (error) {
      failedGuilds.push({
        url,
        error: error.message || String(error)
      });

      console.warn(`Failed to process ${url}:`, error);
    }

    await sleep(DELAY_MS);
  }

  console.log("Done.");

  console.log("Download recap:");
  console.log(`Successful: ${successfulGuilds.length}`);
  console.log(`Failed: ${failedGuilds.length}`);

  console.log("Successful guilds:");
  if (successfulGuilds.length > 0) {
    console.table(successfulGuilds);
  } else {
    console.log("No successful guilds.");
  }

  console.log("Failed guilds:");
  if (failedGuilds.length > 0) {
    console.table(failedGuilds);
  } else {
    console.log("No failed guilds.");
  }
})();