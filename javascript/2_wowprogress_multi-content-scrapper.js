(async () => {
  const GUILD_URLS = [
    "https://www.wowprogress.com/guild/eu/ragnaros/Revolutionist",
    "https://www.wowprogress.com/guild/eu/tarren-mill/Misty+Moon",
    "https://www.wowprogress.com/guild/eu/aggra/Nefastus",
    "https://www.wowprogress.com/guild/eu/kazzak/Solid+Lads",
    "https://www.wowprogress.com/guild/eu/silvermoon/Proper+Guild+Name",
    "https://www.wowprogress.com/guild/eu/draenor/Rancour",
    "https://www.wowprogress.com/guild/eu/draenor/Reflection",
    "https://www.wowprogress.com/guild/eu/kazzak/Santa+Maria",
    "https://www.wowprogress.com/guild/eu/tarren-mill/Kodeks",
    "https://www.wowprogress.com/guild/eu/twisting-nether/CMT",
    "https://www.wowprogress.com/guild/eu/argent-dawn/Welcome",
    "https://www.wowprogress.com/guild/eu/twisting-nether/Ascendancy",
    "https://www.wowprogress.com/guild/eu/blackmoore/Myth",
    "https://www.wowprogress.com/guild/eu/well-of-eternity/Project+One",
    "https://www.wowprogress.com/guild/eu/vashj/Forbidden",
    "https://www.wowprogress.com/guild/eu/blackmoore/Die+Gummib%C3%A4renbande",
    "https://www.wowprogress.com/guild/eu/tarren-mill/Axon+Terminal",
    "https://www.wowprogress.com/guild/eu/antonidas/SeriousBusiness",
    "https://www.wowprogress.com/guild/eu/thrall/evicted",
    "https://www.wowprogress.com/guild/eu/twisting-nether/WatchYourFeet",
    "https://www.wowprogress.com/guild/eu/stormreaver/Noni",
    "https://www.wowprogress.com/guild/eu/eredar/Shattered",
    "https://www.wowprogress.com/guild/eu/kazzak/No+Shame",
    "https://www.wowprogress.com/guild/eu/blackmoore/Spirits+Rising",
    "https://www.wowprogress.com/guild/eu/kazzak/Tuju",
    "https://www.wowprogress.com/guild/eu/ragnaros/Bravo+Six",
    "https://www.wowprogress.com/guild/eu/eredar/Shattrath+Island",
    "https://www.wowprogress.com/guild/eu/tarren-mill/Huhuholics",
    "https://www.wowprogress.com/guild/eu/blackhand/Epos",
    "https://www.wowprogress.com/guild/eu/thrall/The+Daysleepers",
    "https://www.wowprogress.com/guild/eu/kazzak/PoEballys",
    "https://www.wowprogress.com/guild/eu/kazzak/Profanities",
    "https://www.wowprogress.com/guild/eu/draenor/Ninth+Order",
    "https://www.wowprogress.com/guild/eu/argent-dawn/Epoch",
    "https://www.wowprogress.com/guild/eu/kazzak/Hindsight",
    "https://www.wowprogress.com/guild/eu/burning-legion/Encore",
    "https://www.wowprogress.com/guild/eu/draenor/Rhythm",
    "https://www.wowprogress.com/guild/eu/tarren-mill/Persistence",
    "https://www.wowprogress.com/guild/eu/blackhand/Retreat",
    "https://www.wowprogress.com/guild/eu/drak-thul/Spectrum",
    "https://www.wowprogress.com/guild/eu/twisting-nether/Indecisive",
    "https://www.wowprogress.com/guild/eu/kazzak/Dont+Heal+Phase+One",
    "https://www.wowprogress.com/guild/eu/tarren-mill/Neverland",
    "https://www.wowprogress.com/guild/eu/tarren-mill/Clarity",
    "https://www.wowprogress.com/guild/eu/twisting-nether/A+Friends+Guild",
    "https://www.wowprogress.com/guild/eu/quel-thalas/Iris",
    "https://www.wowprogress.com/guild/eu/twisting-nether/Revelations",
    "https://www.wowprogress.com/guild/eu/twisting-nether/Rhapsody",
    "https://www.wowprogress.com/guild/eu/ragnaros/Low+Expectations",
    "https://www.wowprogress.com/guild/eu/silvermoon/Death+and+Glory",
    "https://www.wowprogress.com/guild/eu/ragnaros/Interstellar+Bum+Orcs",
    "https://www.wowprogress.com/guild/eu/twisting-nether/TED",
    "https://www.wowprogress.com/guild/eu/thrall/Doomed",
    "https://www.wowprogress.com/guild/eu/tarren-mill/Do+not+even",
    "https://www.wowprogress.com/guild/eu/blackrock/Unic",
    "https://www.wowprogress.com/guild/eu/ragnaros/Aotic",
    "https://www.wowprogress.com/guild/eu/twisting-nether/The+Reckless",
    "https://www.wowprogress.com/guild/eu/twisting-nether/W+a+s+h+e+d",
    "https://www.wowprogress.com/guild/eu/stormrage/Avalerion",
    "https://www.wowprogress.com/guild/eu/stormreaver/TURBO+SAAB",
    "https://www.wowprogress.com/guild/eu/tarren-mill/Der+er+tilbud+i+Netto",
    "https://www.wowprogress.com/guild/eu/ragnaros/Deep+Tranquility",
    "https://www.wowprogress.com/guild/eu/twisting-nether/Salty+Tears",
    "https://www.wowprogress.com/guild/eu/kazzak/Reversio",
    "https://www.wowprogress.com/guild/eu/burning-blade/Salt+Mines",
    "https://www.wowprogress.com/guild/eu/blackhand/Huskies+eSports",
    "https://www.wowprogress.com/guild/eu/draenor/Ad+Elysium",
    "https://www.wowprogress.com/guild/eu/ragnaros/The+High+Council",
    "https://www.wowprogress.com/guild/eu/tarren-mill/Drama",
    "https://www.wowprogress.com/guild/eu/blackrock/styx",
    "https://www.wowprogress.com/guild/eu/tarren-mill/R+e+t+i+r+e+d",
    "https://www.wowprogress.com/guild/eu/stormscale/Erased",
    "https://www.wowprogress.com/guild/eu/burning-blade/Eternal+Shadows",
    "https://www.wowprogress.com/guild/eu/blackhand/Gravity",
    "https://www.wowprogress.com/guild/eu/sylvanas/Mercy+Killers",
    "https://www.wowprogress.com/guild/eu/kazzak/From+Ashes",
    "https://www.wowprogress.com/guild/eu/kazzak/TERRA",
    "https://www.wowprogress.com/guild/eu/blackrock/Flawless",
    "https://www.wowprogress.com/guild/eu/blackhand/%C3%86VUM",
    "https://www.wowprogress.com/guild/eu/eredar/Zwei+K%C3%B6lsch+bitte",
    "https://www.wowprogress.com/guild/eu/ragnaros/Ring+%C3%85klagarn",
    "https://www.wowprogress.com/guild/eu/blackmoore/Keine+Ahnung",
    "https://www.wowprogress.com/guild/eu/tarren-mill/RETRY",
    "https://www.wowprogress.com/guild/eu/stormscale/Deposit+Coin",
    "https://www.wowprogress.com/guild/eu/kazzak/Synergize",
    "https://www.wowprogress.com/guild/eu/burning-legion/The+Seekers",
    "https://www.wowprogress.com/guild/eu/kazzak/Pixelbased+Lifeforms",
    "https://www.wowprogress.com/guild/eu/draenor/Bestyrelsen",
    "https://www.wowprogress.com/guild/eu/blackhand/Banelings",
    "https://www.wowprogress.com/guild/eu/dentarg/The+Hex+Pistols",
    "https://www.wowprogress.com/guild/eu/draenor/Cor+Fortium",
    "https://www.wowprogress.com/guild/eu/magtheridon/Foundation",
    "https://www.wowprogress.com/guild/eu/twisting-nether/OG+Feedback",
    "https://www.wowprogress.com/guild/eu/blackrock/TeamSpirit",
    "https://www.wowprogress.com/guild/eu/azjol-nerub/Average+Pillagers",
    "https://www.wowprogress.com/guild/eu/dun-morogh/Helden+in+Pyjamas",
    "https://www.wowprogress.com/guild/eu/stormreaver/Kultzipuppelit"
  ];

  const DELAY_MS = 500;

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

  const getWorldRank = (doc) => {
    // Example HTML:
    // <span class="rank legendary"><span class="rank">351</span></span>

    const rankNode =
      doc.querySelector("span.rank.legendary > span.rank")
      ?? [...doc.querySelectorAll("span.rank > span.rank")]
        .find(node => /^\d+$/.test(node.innerText.trim()));

    const rankText = rankNode?.innerText.trim() ?? "";
    const rankNumber = Number(rankText.replace(/[^\d]/g, ""));

    return Number.isFinite(rankNumber) && rankNumber > 0
      ? rankNumber
      : null;
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
      const rank = getWorldRank(doc);

      const guildProfile = {
        url,
        guild_name: guildName,
        rank,
        language: cleanLanguage(getText(profile, "div.language")),
        raids_per_week: cleanRaidsPerWeek(getText(profile, "div.raids_week")),
        description: getText(profile, "div.guildDescription"),
        recruitment: getRecruitment(profile, doc)
      };

      const filename = `${safeFilename(guildName)}.json`;

      downloadJson(filename, guildProfile);

      successfulGuilds.push({
        guild_name: guildName,
        rank,
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