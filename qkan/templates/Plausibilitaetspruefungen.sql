-- DELETE FROM pruefsql;
-- Hinweis: printf() benötigt Textkonstanten mit ""
INSERT INTO pruefsql (gruppe, warntext, warntyp, warnlevel, sql, layername, attrname)
SELECT pn.gruppe, pn.warntext, pn.warntyp, pn.warnlevel, pn.sql, pn.layername, pn.attrname FROM
(   SELECT column1 AS gruppe, column2 AS warntext, column3 AS warntyp, column4 AS warnlevel, column5 AS sql, column6 AS layername, column7 AS attrname FROM 
    (   VALUES
('Netzstruktur', 'Schacht oben mehr als 1.0 m von Haltungsende entfernt', 'Fehler', 9, 
    'SELECT haltnam, ''Schacht oben mehr als 1.0 m von Haltungsende entfernt'' AS bemerkung
    FROM haltungen AS ha
    LEFT JOIN schaechte AS so ON ha.schoben = so.schnam
    WHERE within(so.geop, buffer(pointn(ha.geom,1), 1.0)) <> 1 AND (haltungstyp = ''Haltung'' OR haltungstyp IS NULL)',
 'Haltungen', 'haltnam'),
('Netzstruktur', 'Schacht unten mehr als 1.0 m von Haltungsende entfernt', 'Fehler', 9, 
    'SELECT haltnam, ''Schacht unten mehr als 1.0 m von Haltungsende entfernt'' AS bemerkung
    FROM haltungen AS ha
    LEFT JOIN schaechte AS su ON ha.schunten = su.schnam
    WHERE within(su.geop, buffer(pointn(ha.geom,-1), 1.0)) <> 1 AND (haltungstyp = ''Haltung'' OR haltungstyp IS NULL)',
 'Haltungen', 'haltnam'),
('Geoobjekte', 'Haltung ohne graphisches Linienobjekt', 'Fehler', 9,
    'SELECT haltnam, printf("Datensatz in Layer ""Haltungen"" in %d Datensätzen hat kein graphisches Linienobjekt (nur max. 5 Datensätze angezeigt)", (SELECT count(*) FROM haltungen WHERE geom IS NULL AND (haltungstyp = ''Haltung'' OR haltungstyp IS NULL))) AS bemerkung
FROM haltungen
WHERE geom IS NULL AND (haltungstyp = ''Haltung'' OR haltungstyp IS NULL) LIMIT 5',
 'Haltungen', 'haltnam'),
('Geoobjekte', 'Pumpen ohne graphisches Linienobjekt', 'Fehler', 9,
    'SELECT haltnam, printf("Datensatz in Layer ""Pumpen"" in %d Datensätzen hat kein graphisches Linienobjekt (nur max. 5 Datensätze angezeigt)", (SELECT count(*) FROM haltungen WHERE geom IS NULL AND (haltungstyp = ''Pumpe''))) AS bemerkung
FROM haltungen
WHERE geom IS NULL AND (haltungstyp = ''Pumpe'') LIMIT 5',
 'Pumpen', 'haltnam'),
('Geoobjekte', 'Wehr ohne graphisches Linienobjekt', 'Fehler', 9,
    'SELECT haltnam, printf("Datensatz in Layer ""Wehre"" in %d Datensätzen hat kein graphisches Linienobjekt (nur max. 5 Datensätze angezeigt)", (SELECT count(*) FROM haltungen WHERE geom IS NULL AND (haltungstyp = ''Wehr''))) AS bemerkung
FROM haltungen
WHERE geom IS NULL AND (haltungstyp = ''Wehr'') LIMIT 5',
 'Haltungen', 'haltnam'),
('Geoobjekte', 'Schacht ohne graphisches Punktobjekt', 'Fehler', 9,
    'SELECT schnam, printf("Datensatz in Layer ""Schächte"" in %d Datensätzen hat kein graphisches  Punktobjekt (nur max. 5 Datensätze angezeigt)", (SELECT count(*) FROM schaechte WHERE geop IS NULL AND (schachttyp = ''Schacht'' OR schachttyp IS NULL))) AS bemerkung
FROM schaechte
WHERE geop IS NULL AND (schachttyp = ''Schacht'' OR schachttyp IS NULL) LIMIT 5',
 'Schächte', 'schnam'),
('Geoobjekte', 'Auslass ohne graphisches Punktobjekt', 'Fehler', 9,
    'SELECT schnam, printf("Datensatz in Layer ""Auslässe"" in %d Datensätzen hat kein graphisches  Punktobjekt (nur max. 5 Datensätze angezeigt)", (SELECT count(*) FROM schaechte WHERE geop IS NULL AND (schachttyp = ''Auslass''))) AS bemerkung
FROM schaechte
WHERE geop IS NULL AND (schachttyp = ''Auslass'') LIMIT 5',
 'Auslässe', 'schnam'),
('Geoobjekte', 'Speicher ohne graphisches Punktobjekt', 'Fehler', 9,
    'SELECT schnam, printf("Datensatz in Layer ""Speicher"" in %d Datensätzen hat kein graphisches  Punktobjekt (nur max. 5 Datensätze angezeigt)", (SELECT count(*) FROM schaechte WHERE geop IS NULL AND (schachttyp = ''Speicher'' OR schachttyp IS NULL))) AS bemerkung
FROM schaechte
WHERE geop IS NULL AND (schachttyp = ''Speicher'' OR schachttyp IS NULL) LIMIT 5',
 'Speicher', 'schnam'),
('Geoobjekte', 'Kein Flächenobjekt', 'Fehler', 9,
    'SELECT flnam, printf("Datensatz in Layer ""Flächen"" in %d Datensätzen hat kein graphisches Flächenobjekt (nur max. 5 Datensätze angezeigt)", (SELECT count(*) FROM flaechen WHERE geom IS NULL)) AS bemerkung
FROM flaechen
WHERE geom IS NULL LIMIT 5',
 'Flächen', 'flnam'),
('Geoobjekte', 'Kein Flächenobjekt', 'Fehler', 9,
    'SELECT flnam, printf("Datensatz in Layer ""Haltungsflächen"" in %d Datensätzen hat kein Flächenobjekt (nur max. 5 Datensätze angezeigt)", (SELECT count(*) FROM tezg WHERE geom IS NULL)) AS bemerkung
FROM tezg
WHERE geom IS NULL LIMIT 5',
 'Haltungsflächen', 'flnam'),
('Geoobjekte', 'Flächenanbindung ohne graphisches Linienobjekt', 'Fehler', 9,
    'SELECT flnam, printf("Datensatz in Layer ""Anbindungen Flächen"" in %d Datensätzen hat kein graphisches Linienobjekt (nur max. 5 Datensätze angezeigt)", (SELECT count(*) FROM linkfl WHERE geom IS NULL)) AS bemerkung
FROM linkfl
WHERE geom IS NULL LIMIT 5',
 'Anbindungen Flächen', 'flnam'),
('HYSTEM-EXTRAN', 'Abflussparameter fehlen', 'Fehler', 9,
    'SELECT f1.flnam,
        printf("Abflussparameter ""%s"" wird in Layer ""Flächen"" verwendet, fehlt aber in Referenztabelle ""Abflussparameter HE"" bzw. ""... KP"" in %d Datensätzen (nur max. 5 Datensätze angezeigt)", 
            f1.abflussparameter, (
			SELECT count(*)
			FROM flaechen AS f2
			WHERE f2.abflussparameter = f1.abflussparameter
			)) AS bemerkung
    FROM flaechen AS f1
    LEFT JOIN abflussparameter ON f1.abflussparameter = abflussparameter.apnam
    WHERE abflussparameter.pk IS NULL
    GROUP BY f1.flnam LIMIT 5', 
 'Abflussparameter', 'flnam'),
('HYSTEM-EXTRAN', 'Schwerpunktlaufzeiten fehlen', 'Fehler', 9, 
    'SELECT flnam,
        printf("Spalte ""fliesszeitflaeche"" in Layer ""Anbindungen Flächen"" in %d Datensätzen leer (nur max. 5 Datensätze angezeigt)", (SELECT count(*) FROM linkfl WHERE fliesszeitflaeche IS NULL)) AS bemerkung
    FROM linkfl
    WHERE fliesszeitflaeche IS NULL LIMIT 5',
 'Anbindungen Flächen', 'flnam'),
('HYSTEM-EXTRAN', 'Simulationsstatus fehlt oder nicht in Tabelle "Simulationsstatus"', 'Fehler', 9,
    'SELECT s.schnam,
        printf("Spalte simstatus = %s in Spalte leer oder nicht in Simulationsstatus (nur 1 exemplarisch aufgelistet!)", s.simstatus) AS bemerkung
    FROM schaechte AS s
    LEFT JOIN simulationsstatus AS u ON s.simstatus = u.bezeichnung
    WHERE u.bezeichnung IS NULL GROUP BY s.simstatus', 
 'Schächte', 'schnam'),
('HYSTEM-EXTRAN', 'Neigungsklasse fehlt', 'Fehler', 9,
    'SELECT flnam,
        printf("Spalte ""neigkl"" in Layer ""Flächen"" in %d Datensätzen leer (nur max. 5 Datensätze angezeigt)", (SELECT count(*) FROM flaechen WHERE neigkl IS NULL)) AS bemerkung
    FROM flaechen
    WHERE neigkl IS NULL LIMIT 5',
 'Flächen', 'flnam'),
('HYSTEM-EXTRAN', 'Profil fehlt in Layer "Profile"', 'Fehler', 9,
    'SELECT h.haltnam,
        printf("Profil ''%s'' fehlt in Layer Profile", h.profilnam) AS bemerkung 
    FROM haltungen AS h
    LEFT JOIN profile AS p
    ON h.profilnam = p.profilnam
    WHERE p.profilnam IS NULL AND (haltungstyp = ''Haltung'' OR haltungstyp IS NULL)
    GROUP BY h.profilnam',
 'Haltungen', 'haltnam'),
('Netzstruktur', 'Schachtnamen doppelt', 'Fehler', 9,
    'SELECT schnam,
        printf("Schachtnamen doppelt in Layer ""Schächte"" in %d Datensätzen (nur max. 5 Datensätze angezeigt)", (SELECT count(*) FROM (SELECT schnam FROM schaechte GROUP BY schnam HAVING count(*) > 1))) AS bemerkung
    FROM (SELECT schnam FROM schaechte GROUP BY schnam HAVING count(*) > 1) LIMIT 5', 
 'Schächte', 'schnam'),
('Netzstruktur', 'Haltungsnamen doppelt', 'Fehler', 9,
    'SELECT haltnam,
        printf("Haltungsnamen doppelt in Layer ""Haltungen"" in %d Datensätzen (nur max. 5 Datensätze angezeigt)", (SELECT count(*) FROM (SELECT haltnam FROM haltungen GROUP BY haltnam HAVING count(*) > 1))) AS bemerkung
    FROM (SELECT haltnam FROM haltungen GROUP BY haltnam HAVING count(*) > 1) LIMIT 5', 
 'Haltungen', 'haltnam'),
('Kreuzende Haltungen', 'Kreuzende Haltungen', 'Warnung', 6, 
    'SELECT
         haltna1 AS haltnam, 
         printf("Theoretischer Abstand zu Haltung %s beträgt d = %.2f", haltna2, COALESCE(abstkreuz, d3)) as bemerkung
    FROM (
    SELECT 
      haltna1, haltna2, hoehob, hoehun, 
      abs((p3x-p1x)*ex+(p3y-p1y)*ey+(p3z-p1z)*ez)/SQRT(ex*ex+ey*ey+ez*ez) AS abstkreuz, 
      abs(L13/SQRT(L12))         AS abstpar,
      ((sx-p1x)*(p2x-p1x)+(sy-p1y)*(p2y-p1y))*((sx-p2x)*(p2x-p1x)+(sy-p2y)*(p2y-p1y)) AS d1, 
      ((sx-p3x)*(p4x-p3x)+(sy-p3y)*(p4y-p3y))*((sx-p4x)*(p4x-p3x)+(sy-p4y)*(p4y-p3y)) AS d2, 
      MAX(0, L12, L13, L14)-MIN(0, L12, L13, L14)-ABS(L12)-ABS(L34)                   AS d3
    FROM (
      SELECT 
        haltna1, haltna2, hoehob, hoehun, 
        p1x, p1y, p1z, p2x, p2y, p2z, p3x, p3y, p3z, p4x, p4y, p4z, ex, ey, ez,
        CASE WHEN abs(det) > 0.000001 * bet THEN
          p1x+(p2x-p1x)*((p3x-p1x)*(p3y-p4y)-(p3y-p1y)*(p3x-p4x))/det ELSE NULL END     AS sx,
        CASE WHEN abs(det) > 0.000001 * bet THEN
          p1y+(p2y-p1y)*((p3x-p1x)*(p3y-p4y)-(p3y-p1y)*(p3x-p4x))/det ELSE NULL END     AS sy,
        ((p2x-p1x)*(p2x-p1x)+(p2y-p1y)*(p2y-p1y))                                       AS L12,
        ((p3x-p1x)*(p2x-p1x)+(p3y-p1y)*(p2y-p1y))                                       AS L13,
        ((p4x-p1x)*(p2x-p1x)+(p4y-p1y)*(p2y-p1y))                                       AS L14,
        ((p4x-p3x)*(p2x-p1x)+(p4y-p3y)*(p2y-p1y))                                       AS L34
      FROM (
        SELECT 
          haltna1, haltna2, hoehob, hoehun, 
          p1x, p1y, p1z, p2x, p2y, p2z, p3x, p3y, p3z, p4x, p4y, p4z, 
          (p2y-p1y)*(p4z-p3z)-(p2z-p1z)*(p4y-p3y) AS ex, 
          (p2z-p1z)*(p4x-p3x)-(p2x-p1x)*(p4z-p3z) AS ey,
          (p2x-p1x)*(p4y-p3y)-(p2y-p1y)*(p4x-p3x) AS ez,
          ((p2x-p1x)*(p3y-p4y)-(p2y-p1y)*(p3x-p4x)) AS det,
          ((p2x-p1x)*(p3x-p4x)+(p2y-p1y)*(p3y-p4y)) AS bet
        FROM (
          SELECT
            ho.haltnam            AS haltna1, 
            hu.haltnam            AS haltna2, 
            ho.hoehe              AS hoehob, 
            hu.hoehe              AS hoehun, 
            x(PointN(ho.geom,1))  AS p1x, 
            y(PointN(ho.geom,1))  AS p1y, 
            ho.zoben              AS p1z, 
            x(PointN(ho.geom,-1)) AS p2x, 
            y(PointN(ho.geom,-1)) AS p2y, 
            ho.zunten             AS p2z, 
            x(PointN(hu.geom,1))  AS p3x, 
            y(PointN(hu.geom,1))  AS p3y, 
            hu.zoben              AS p3z, 
            x(PointN(hu.geom,-1)) AS p4x, 
            y(PointN(hu.geom,-1)) AS p4y, 
            hu.zunten             AS p4z
          FROM (
            SELECT
              ha.haltnam AS haltnam, 
              ha.schoben AS schoben,
              ha.schunten AS schunten,
              ha.geom AS geom, 
              COALESCE(ha.sohleoben, so.sohlhoehe)  + COALESCE(ha.hoehe, ha.breite)*0.5 AS zoben, 
              COALESCE(ha.sohleunten, su.sohlhoehe) + COALESCE(ha.hoehe, ha.breite)*0.5 AS zunten,
              COALESCE(ha.hoehe, ha.breite) AS durchm, 
              CASE WHEN COALESCE(ha.hoehe, 0) = 0 THEN ha.breite ELSE ha.hoehe END AS hoehe
            FROM haltungen AS ha 
            INNER JOIN schaechte AS so 
            ON ha.schoben = so.schnam
            INNER JOIN schaechte AS su 
            ON ha.schunten = su.schnam
            WHERE (haltungstyp = ''Haltung'' OR haltungstyp IS NULL)
          ) AS ho 
          INNER JOIN (
            SELECT
              ha.haltnam AS haltnam, 
              ha.schoben AS schoben,
              ha.schunten AS schunten,
              ha.geom AS geom, 
              COALESCE(ha.sohleoben, so.sohlhoehe)  + COALESCE(ha.hoehe, ha.breite)*0.5 AS zoben, 
              COALESCE(ha.sohleunten, su.sohlhoehe) + COALESCE(ha.hoehe, ha.breite)*0.5 AS zunten,
              COALESCE(ha.hoehe, ha.breite) AS durchm, 
              CASE WHEN COALESCE(ha.hoehe, 0) = 0 THEN ha.breite ELSE ha.hoehe END AS hoehe
            FROM haltungen AS ha 
            INNER JOIN schaechte AS so 
            ON ha.schoben = so.schnam
            INNER JOIN schaechte AS su 
            ON ha.schunten = su.schnam
            WHERE (haltungstyp = ''Haltung'' OR haltungstyp IS NULL)
          ) AS hu
          ON Distance(ho.geom, hu.geom) < 0.5 + (ho.durchm + hu.durchm) / 2.0
          WHERE
            ho.haltnam <> hu.haltnam AND 
            ho.schoben not in (hu.schoben, hu.schunten) AND 
            ho.schunten not in (hu.schoben, hu.schunten) AND 
            ho.zoben + ho.zunten >= hu.zoben + hu.zunten
          )
        )
      )
    WHERE
    CASE WHEN d1 IS NOT NULL AND d1 <= 0 AND d2 <= 0
        THEN abstkreuz <= (hoehob + hoehun) / 2.0 + 0.5
    WHEN d1 IS NULL AND d3 <= 0
        THEN abstpar <= (hoehob + hoehun) / 2.0 + 0.5
    ELSE FALSE END)',
 'Haltungen', 'haltnam'),
('Zustandsklassen', 'Der Schadenskode hat mehr als 3 Zeichen', 'Fehler', 9,
    'SELECT pk , ''Der Schadenskode hat mehr als 3 Zeichen'' AS bemerkung
    FROM Untersuchdat_haltung
    WHERE LENGTH(kuerzel) IS NOT 3',
 'Untersuchungsdaten Haltung', 'pk'),
('Zustandsklassen', 'Haltungsname doppelt', 'Fehler', 9,
    'SELECT COUNT(*) AS "Count", pk , ''Haltungsname doppelt'' AS bemerkung
    FROM haltungen group by haltnam having count(*)>1 ',
 'Haltungen', 'pk'),
('Zustandsklassen', 'Schachtname doppelt', 'Fehler', 9,
    'SELECT COUNT(*) AS "Count", pk , ''Haltungsname doppelt'' AS bemerkung
    FROM schaechte group by schnam having count(*)>1 ',
 'Schächte', 'pk'),
('Zustandsklassen', 'Der Schadenskode hat mehr als 3 Zeichen', 'Fehler', 9,
    'SELECT pk , ''Der Schadenskode hat mehr als 3 Zeichen'' AS bemerkung
    FROM Untersuchdat_schacht
    WHERE LENGTH(kuerzel) IS NOT 3',
 'Untersuchungsdaten Schacht', 'pk'),
('Zustandsklassen', 'Fehlende Angabe der Streckenschadensnummer', 'Fehler', 9,
    'SELECT pk , ''Fehlende Angabe der Streckenschadensnummer'' AS bemerkung
    FROM Untersuchdat_haltung
    WHERE streckenschaden IS NOT "not found" and streckenschaden_lfdnr IS 0',
 'Untersuchungsdaten Haltung', 'pk'),
('Zustandsklassen', 'Fehlende Angabe des Streckenschadens', 'Fehler', 9,
    'SELECT pk , ''Fehlende Angabe des Streckenschadens'' AS bemerkung
    FROM Untersuchdat_haltung
    WHERE (streckenschaden IS "not found" or streckenschaden IS NULL) and streckenschaden_lfdnr IS NOT 0',
 'Untersuchungsdaten Haltung', 'pk'), 
('Zustandsklassen', 'Das vergebene Schadenskürzel prüfen', 'Fehler', 9,
    'SELECT pk , ''Das vergebene Schadenskürzel prüfen'' AS bemerkung
    FROM Untersuchdat_haltung
    WHERE  Untersuchdat_haltung.kuerzel
							not in (select reflist_zustand.hauptcode from reflist_zustand WHERE art = "Haltung DWA")
							AND  Untersuchdat_haltung.untersuchhal in (select haltungen_untersucht.haltnam from haltungen_untersucht WHERE datenart = "DWA")',
 'Untersuchungsdaten Haltung', 'pk'), 
('Zustandsklassen', 'Das vergebene Schadenskürzel prüfen', 'Fehler', 9,
    'SELECT pk , ''Das vergebene Schadenskürzel prüfen'' AS bemerkung
    FROM Untersuchdat_haltung
    WHERE  Untersuchdat_haltung.kuerzel
							not in (select reflist_zustand.hauptcode from reflist_zustand WHERE art = "Haltung ISYBAU")
							AND  Untersuchdat_haltung.untersuchhal in (select haltungen_untersucht.haltnam from haltungen_untersucht WHERE datenart = "ISYBAU")',
 'Untersuchungsdaten Haltung', 'pk'), 
('Zustandsklassen', 'Das vergebene Schadenskürzel prüfen', 'Fehler', 9,
    'SELECT pk , ''Das vergebene Schadenskürzel prüfen'' AS bemerkung
    FROM Untersuchdat_schacht
    WHERE  Untersuchdat_schacht.kuerzel
							not in (select reflist_zustand.hauptcode from reflist_zustand WHERE art = "Schacht DWA")
							AND  Untersuchdat_schacht.untersuchsch in (select schaechte_untersucht.schnam from schaechte_untersucht WHERE datenart = "DWA")',
 'Untersuchungsdaten Schacht', 'pk'), 
('Zustandsklassen', 'Das vergebene Schadenskürzel prüfen', 'Fehler', 9,
    'SELECT pk , ''Das vergebene Schadenskürzel prüfen'' AS bemerkung
    FROM Untersuchdat_schacht
    WHERE Untersuchdat_schacht.kuerzel
							not in (select reflist_zustand.hauptcode from reflist_zustand WHERE art = "Schacht ISYBAU")
							AND  Untersuchdat_schacht.untersuchsch in (select schaechte_untersucht.schnam from schaechte_untersucht WHERE datenart = "ISYBAU")',
 'Untersuchungsdaten Schacht', 'pk'), 
('Zustandsklassen', 'Die Charakteriserung 1 prüfen', 'Fehler', 9,
    'SELECT pk , ''Die Charakteriserung 1 prüfen'' AS bemerkung
    FROM Untersuchdat_haltung
    WHERE Untersuchdat_haltung.kuerzel
							in (select reflist_zustand.hauptcode from reflist_zustand WHERE art = "Haltung DWA")
							AND Untersuchdat_haltung.charakt1
							not in (select reflist_zustand.charakterisierung1 from reflist_zustand WHERE reflist_zustand.charakterisierung1 like Untersuchdat_haltung.charakt1 AND Untersuchdat_haltung.kuerzel = reflist_zustand.hauptcode)
							AND  Untersuchdat_haltung.untersuchhal in (select haltungen_untersucht.haltnam from haltungen_untersucht WHERE datenart = "DWA")',
 'Untersuchungsdaten Haltung', 'pk'), 
('Zustandsklassen', 'Die Charakteriserung 1 prüfen', 'Fehler', 9,
    'SELECT pk , ''Die Charakteriserung 1 prüfen'' AS bemerkung
    FROM Untersuchdat_haltung
    WHERE Untersuchdat_haltung.kuerzel
							in (select reflist_zustand.hauptcode from reflist_zustand WHERE art = "Haltung ISYBAU")
							AND Untersuchdat_haltung.charakt1
							not in (select reflist_zustand.charakterisierung1 from reflist_zustand WHERE reflist_zustand.charakterisierung1 like Untersuchdat_haltung.charakt1 AND Untersuchdat_haltung.kuerzel = reflist_zustand.hauptcode)
							AND  Untersuchdat_haltung.untersuchhal in (select haltungen_untersucht.haltnam from haltungen_untersucht WHERE datenart = "ISYBAU")',
 'Untersuchungsdaten Haltung', 'pk'), 
('Zustandsklassen', 'Die Charakteriserung 1 prüfen', 'Fehler', 9,
    'SELECT pk , ''Die Charakteriserung 1 prüfen'' AS bemerkung
    FROM Untersuchdat_schacht
    WHERE Untersuchdat_schacht.kuerzel
							in (select reflist_zustand.hauptcode from reflist_zustand WHERE art = "Schacht DWA")
							AND Untersuchdat_schacht.charakt1
							not in (select reflist_zustand.charakterisierung1 from reflist_zustand WHERE reflist_zustand.charakterisierung1 like Untersuchdat_schacht.charakt1 AND Untersuchdat_schacht.kuerzel = reflist_zustand.hauptcode)
							AND  Untersuchdat_schacht.untersuchsch in (select schaechte_untersucht.schnam from schaechte_untersucht WHERE datenart = "DWA")',
 'Untersuchungsdaten Schacht', 'pk'), 
('Zustandsklassen', 'Die Charakteriserung 1 prüfen', 'Fehler', 9,
    'SELECT pk , ''Die Charakteriserung 1 prüfen'' AS bemerkung
    FROM Untersuchdat_schacht
    WHERE Untersuchdat_schacht.kuerzel
							in (select reflist_zustand.hauptcode from reflist_zustand WHERE art = "Schacht ISYBAU")
							AND Untersuchdat_schacht.charakt1
							not in (select reflist_zustand.charakterisierung1 from reflist_zustand WHERE reflist_zustand.charakterisierung1 like Untersuchdat_schacht.charakt1 AND Untersuchdat_schacht.kuerzel = reflist_zustand.hauptcode)
							AND  Untersuchdat_schacht.untersuchsch in (select schaechte_untersucht.schnam from schaechte_untersucht WHERE datenart = "ISYBAU")',
 'Untersuchungsdaten Schacht', 'pk'), 
('Zustandsklassen', 'Die Charakteriserung 2 prüfen', 'Fehler', 9,
    'SELECT pk , ''Die Charakteriserung 2 prüfen'' AS bemerkung
    FROM Untersuchdat_haltung
    WHERE Untersuchdat_haltung.kuerzel
							in (select reflist_zustand.hauptcode from reflist_zustand WHERE art = "Haltung DWA")
							AND Untersuchdat_haltung.charakt2
							not in (select reflist_zustand.charakterisierung2 from reflist_zustand WHERE reflist_zustand.charakterisierung1 like Untersuchdat_haltung.charakt1 AND Untersuchdat_haltung.kuerzel = reflist_zustand.hauptcode)
							AND  Untersuchdat_haltung.untersuchhal in (select haltungen_untersucht.haltnam from haltungen_untersucht WHERE datenart = "DWA")',
 'Untersuchungsdaten Haltung', 'pk'), 
('Zustandsklassen', 'Die Charakteriserung 2 prüfen', 'Fehler', 9,
    'SELECT pk , ''Die Charakteriserung 2 prüfen'' AS bemerkung
    FROM Untersuchdat_haltung
    WHERE Untersuchdat_haltung.kuerzel
							in (select reflist_zustand.hauptcode from reflist_zustand WHERE art = "Haltung ISYBAU")
							AND Untersuchdat_haltung.charakt2
							not in (select reflist_zustand.charakterisierung2 from reflist_zustand WHERE reflist_zustand.charakterisierung1 like Untersuchdat_haltung.charakt1 AND Untersuchdat_haltung.kuerzel = reflist_zustand.hauptcode)
							AND  Untersuchdat_haltung.untersuchhal in (select haltungen_untersucht.haltnam from haltungen_untersucht WHERE datenart = "ISYBAU")',
 'Untersuchungsdaten Haltung', 'pk'), 
('Zustandsklassen', 'Die Charakteriserung 2 prüfen', 'Fehler', 9,
    'SELECT pk , ''Die Charakteriserung 2 prüfen'' AS bemerkung
    FROM Untersuchdat_schacht
    WHERE Untersuchdat_schacht.kuerzel
							in (select reflist_zustand.hauptcode from reflist_zustand WHERE art = "Schacht DWA")
							AND Untersuchdat_schacht.charakt2
							not in (select reflist_zustand.charakterisierung2 from reflist_zustand WHERE reflist_zustand.charakterisierung1 like Untersuchdat_schacht.charakt1 AND Untersuchdat_schacht.kuerzel = reflist_zustand.hauptcode)
							AND  Untersuchdat_schacht.untersuchsch in (select schaechte_untersucht.schnam from schaechte_untersucht WHERE datenart = "DWA")',
 'Untersuchungsdaten Schacht', 'pk'), 
('Zustandsklassen', 'Die Charakteriserung 2 prüfen', 'Fehler', 9,
    'SELECT pk , ''Die Charakteriserung 2 prüfen'' AS bemerkung
    FROM Untersuchdat_schacht
    WHERE Untersuchdat_schacht.kuerzel
							in (select reflist_zustand.hauptcode from reflist_zustand WHERE art = "Schacht ISYBAU")
							AND Untersuchdat_schacht.charakt2
							not in (select reflist_zustand.charakterisierung2 from reflist_zustand WHERE reflist_zustand.charakterisierung1 like Untersuchdat_schacht.charakt1 AND Untersuchdat_schacht.kuerzel = reflist_zustand.hauptcode)
							AND  Untersuchdat_schacht.untersuchsch in (select schaechte_untersucht.schnam from schaechte_untersucht WHERE datenart = "ISYBAU")',
 'Untersuchungsdaten Schacht', 'pk'), 
('Zustandsklassen', 'Die Angabe vom Bereich prüfen', 'Fehler', 9,
    'SELECT pk , ''Die Angabe vom Bereich prüfen'' AS bemerkung
    FROM Untersuchdat_schacht
    WHERE Untersuchdat_schacht.kuerzel
							in (select reflist_zustand.hauptcode from reflist_zustand WHERE art = "Schacht DWA")
							AND Untersuchdat_schacht.bereich
							not in (select reflist_zustand.bereich from reflist_zustand WHERE reflist_zustand.charakterisierung1 like Untersuchdat_schacht.charakt1 AND Untersuchdat_schacht.kuerzel = reflist_zustand.hauptcode)
							AND  Untersuchdat_schacht.untersuchsch in (select schaechte_untersucht.schnam from schaechte_untersucht WHERE datenart = "DWA")',
 'Untersuchungsdaten Schacht', 'pk'), 
('Zustandsklassen', 'Die Angabe vom Bereich prüfen', 'Fehler', 9,
    'SELECT pk , ''Die Angabe vom Bereich prüfen'' AS bemerkung
    FROM Untersuchdat_schacht
    WHERE Untersuchdat_schacht.kuerzel
							in (select reflist_zustand.hauptcode from reflist_zustand WHERE art = "Schacht ISYBAU")
							AND Untersuchdat_schacht.bereich
							not in (select reflist_zustand.bereich from reflist_zustand WHERE reflist_zustand.charakterisierung1 like Untersuchdat_schacht.charakt1 AND Untersuchdat_schacht.kuerzel = reflist_zustand.hauptcode)
							AND  Untersuchdat_schacht.untersuchsch in (select schaechte_untersucht.schnam from schaechte_untersucht WHERE datenart = "ISYBAU")',
 'Untersuchungsdaten Schacht', 'pk')
    )
) AS pn
LEFT JOIN pruefsql AS ps
ON (pn.gruppe = ps.gruppe AND pn.warntext = ps.warntext)
WHERE ps.warntext IS NULL;
