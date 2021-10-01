SELECT
  name,
  gam.console,
  brd.company AS company,
  metascore,
  userscore,
  (metascore*0.75+(CAST(NULLIF(userscore, 'tbd') AS FLOAT)*10*0.25)) AS custom_score,
  to_date(date, 'MMM d, yyyy')
FROM
  games gam
LEFT JOIN
  brands brd
ON
  gam.console = brd.console