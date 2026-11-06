# Laboratori de transparència social

Demostració reproduïble del projecte d'Emma Cotonat i Donat. **Totes les persones, atributs, preferències i relacions són sintètiques. No són resultats d'un cau ni evidència a favor de les hipòtesis.**

## Obrir el resultat

Descarrega `output/index.html` i obre'l en un navegador. És autònom i funciona sense xarxa, servidors, instal·lacions ni recursos externs. GitHub mostra el codi HTML; per veure el laboratori cal obrir el fitxer descarregat. No s'ha activat GitHub Pages.

## Reproduir

Python 3.10 o posterior, només biblioteca estàndard.

```bash
python simulation/generate.py
python -m unittest discover -s simulation -p 'test_*.py'
```

La llavor per defecte és `20261106`. Es pot canviar amb `--seed 42` o triar un directori de sortida amb `--out /ruta/de/sortida`. Una altra llavor produeix un altre exemple, sense implicar robustesa empírica.

## Model i supòsits

- 12 nodes P01–P12 en tres equips artificials; antiguitat i rol ficticis.
- Sis ítems categòrics, dos per contingut biogràfic, posicional i moral-normatiu. Categories 0–2 sense escala moral.
- Direcció de consulta `i → j`: i consulta j. Grau d'entrada = consultes rebudes.
- Atribució `(observador, persona concernida, ítem)`, diferenciant atribució, desconeixement, reserva i absència.
- Un criteri d'autodescripció queda sense valor deliberadament per provar el tractament de dades no contrastables.
- CSS `R[k,i,j]`: k afirma o nega que i consulta j; `null` és desconegut, no absència.
- El generador afavoreix les consultes a P01, els vincles dins dels equips i la precisió en contacte directe. Redueix la precisió biogràfica sobre P01. Són patrons imposats per mostrar configuracions possibles, no descobriments.
- La probabilitat de manifestar coneixement i la de donar una resposta corroborada varien per àmbit. Els errors poden incorporar projecció.

## Indicadors

`planned`: tots els ítems. `usable`: atribució o desconeixement, excloent reserva/absència. `declared`: atribucions. `comparable`: usable amb criteri. `valid`: atribució amb criteri. `correct`: coincidències exactes.

- Cobertura = declared / usable.
- Cobertura contrastable = valid / comparable.
- Precisió = correct / valid; indefinida si no hi ha atribucions contrastables.
- Corroboració o efectiva operativa = correct / comparable.
- Part atribuïda no corroborada = (valid − correct) / comparable.
- Completitud = usable / planned. Els denominadors sempre s'exporten.

La cobertura és un resum de la transparència percebuda; no substitueix el contingut de les atribucions. La confiança subjectiva no s'utilitza com a percebuda. La diferència entre cobertura contrastable i corroboració és certa per construcció, per tant no és una hipòtesi substantiva.

## CSS

Slice = matriu de k. LAS intersecció = conjunció dels informes de l'emissor i receptor; LAS unió = disjunció. S'utilitza lògica de tres valors: intersecció (0, desconegut) = 0, intersecció (1, desconegut) = desconegut; unió (1, desconegut) = 1 i unió (0, desconegut) = desconegut. Consens = mitjana de judicis vàlids, amb llindar interactiu.

La comparació de tercers amb LAS exclou els vincles en què l'observador és emissor o receptor. Informa de sensibilitat i especificitat respecte de la LAS, que és una referència declarativa. No es confon amb la veritat generadora ni amb dades de conducta observada. El consens no es fa servir com a criteri d'exactitud en aquesta demostració.

## SRM i interpretació

S'exporten perfils d'observador i de persona concernida i un ajust additiu descriptiu per mínims quadrats iteratius sobre la corroboració agregada. Els residus inclouen relació, error i estructura no modelada. **No és un ajust formal del Social Relations Model**, no estima components de variància ni reciprocitat corregida i no produeix p-valors. El disseny de camp requerirà decidir mesures, replicació i estimador adequats.

Les correlacions utilitzen dotze nodes sintètics i són descriptives. No s'assumeix independència de les parelles ni s'infereixen causes o conflictes. La referència majoritària exclou la persona concernida; els empats es resolen pel valor menor. La referència de projecció només inclou casos amb resposta pròpia disponible i n'informa el denominador.

## Fitxers

- `generate.py`: generació, mesures i exportació.
- `template.html`: laboratori autònom amb SVG, selectors i exportació JSON.
- `test_simulation.py`: invariants de mesura, dependència de direcció i reproducció.
- `output/index.html`: laboratori ja generat.
- `output/data.json`: totes les dades i mètriques.
- `output/summary.json`: resum.
- `output/nodes.csv`, `self_reports.csv`, `attributions.csv`, `css.csv`: dades originals en format llarg.

Els índexs numèrics d'observador i persona concernida als CSV són zero-based; l'índex 0 correspon a P01. `null` JSON o camp buit CSV indica valor no disponible; el significat concret s'ha de llegir amb la columna d'estat.

## Relació amb l'eina existent

Aquesta carpeta no modifica el pipeline anterior. La definició d'aquesta demostració segueix el projecte actual, centrat en coneixement interpersonal i percepcions de relacions. Les formulacions històriques del README general, com equiparar transparència a visibilitat del sociograma, no són la definició operativa d'aquest exemple.

## Antecedents

Krackhardt (1987), Cognitive social structures, DOI 10.1016/0378-8733(87)90009-8. Kenny (2020), Interpersonal Perception, 2a ed. Goel, Mason i Watts (2010), DOI 10.1037/a0020697. L'exemple és una implementació exploratòria pròpia i no una reproducció exacta d'aquests estudis.
