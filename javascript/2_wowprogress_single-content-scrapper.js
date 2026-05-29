(() => {
  const profile = document.querySelector("div.guildProfile");

  if (!profile) {
    console.error("No div.guildProfile found on this page.");
    return;
  }

  const getText = (selector) => {
    return profile.querySelector(selector)?.innerText.trim() ?? "";
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

  const getGuildName = () => {
    const h1Text = document.querySelector("h1")?.innerText.trim() ?? "";
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

  const getRecruitment = () => {
    const recrAll = profile.querySelector("span.recrAll");

    if (recrAll) {
      return [
        {
          class: recrAll.innerText.trim() || "all classes"
        }
      ];
    }

    return [...document.querySelectorAll("table.recr tr")]
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

  const guildName = getGuildName();

  const guildProfile = {
    url: window.location.href,
    guild_name: guildName,
    language: cleanLanguage(getText("div.language")),
    raids_per_week: cleanRaidsPerWeek(getText("div.raids_week")),
    description: getText("div.guildDescription"),
    recruitment: getRecruitment()
  };

  const json = JSON.stringify(guildProfile, null, 2);

  const blob = new Blob([json], {
    type: "application/json;charset=utf-8"
  });

  const url = URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = `${safeFilename(guildName)}.json`;
  document.body.appendChild(a);
  a.click();
  a.remove();

  URL.revokeObjectURL(url);

  console.log(`Downloaded ${safeFilename(guildName)}.json`);
  console.log(guildProfile);
})();