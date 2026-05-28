(() => {
  const table = document.querySelector("table.rating");

  if (!table) {
    console.error('No table found with selector: table.rating');
    return;
  }

  const excludedRealmPrefixes = [
    "US",
    "EU (RU)",
    "EU (FR)",
    "EU (ES)",
    "OC",
    "KR",
    "TW"
  ];

  const csvEscape = (value) => {
    const str = String(value ?? "").trim();
    return `"${str.replaceAll('"', '""')}"`;
  };

  const rows = [...table.querySelectorAll("tr")]
    .map(tr => {
      const rank = tr.querySelector("td span.rank")?.innerText.trim() ?? "";
      const guildEl = tr.querySelector("td a.guild");
      const realmEl = tr.querySelector("td a.realm");

      const guildName = guildEl?.innerText.trim() ?? "";
      const realm = realmEl?.innerText.trim() ?? "";
      const href = guildEl?.getAttribute("href") ?? "";

      if (!rank || !guildName || !realm || !href) {
        return null;
      }

      const isExcluded = excludedRealmPrefixes.some(prefix =>
        realm.startsWith(prefix)
      );

      if (isExcluded) {
        return null;
      }

      const link = href.startsWith("http")
        ? href
        : `https://www.wowprogress.com${href}`;

      return [rank, guildName, realm, link];
    })
    .filter(Boolean);

  const csv = [
    ["Rank", "Guild Name", "Realm", "Link"],
    ...rows
  ]
    .map(row => row.map(csvEscape).join(","))
    .join("\n");

  console.log(csv);

  navigator.clipboard.writeText(csv)
    .then(() => console.log(`Copied ${rows.length} guilds to clipboard as CSV.`))
    .catch(() => console.warn("Could not copy to clipboard. CSV was printed above."));
})();