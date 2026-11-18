# Suomenkielinen tutkimusraamattu — v005

Koko suomenkielinen jaeteksti ja sen erilliset lukijahuomautukset, toimitus 18.11.2026.

| Tiedosto | Sisältö |
| --- | --- |
| [bible.json](bible.json) | 66 kirjaa, 1 189 lukua ja 31 170 jaetta. Vain jaetunnisteet ja Raamatun teksti. |
| [footnotes.json](footnotes.json) | 24 531 alaviitettä, kukin omalla tunnisteella ja jaeviitteellä. |
| [crossreferences.json](crossreferences.json) | 55 ristiviiteparia molempiin suuntiin: 110 linkkiä aiheineen. |
| [metadata.json](metadata.json) | Kirjojen nimet ja tunnisteet, versio ja alkuperätiedot. |
| [validation.json](validation.json) | Viennin tarkistustulokset. |
| [SHA256SUMS.json](SHA256SUMS.json) | Aineistotiedostojen SHA-256-tarkistussummat. |

## Käyttö lukijassa

`bible.json` sopii nykyisen lukijan **Settings → Import a text** -toiminnon JSON-muotoon. Anna kieleksi `fi` ja nimeksi esimerkiksi *Suomenkielinen tutkimusraamattu v005*. Valitse tuontiin vain `bible.json`.

Alaviitteet ja ristiviitteet ovat erillisiä aineistoja; niitä ei tuoda Raamatun jakeiksi. Tämä lisäys ei asenna niitä lukijan nykyiseen huomautuskäyttöliittymään eikä muuta julkista käännösvalikkoa.

Yhdistä aineistot tunnisteella `BOOK chapter:verse`, esimerkiksi `GEN 1:1` tai `JHN 14:6`. Raamatun rivissä vastaava tunniste muodostetaan kentistä `book`, `chapter` ja `verse`. Useampi alaviite voi liittyä samaan jakeeseen. Ristiviitteessä `reference` on lähtöjae ja `target` kohdejae; `pair_id` yhdistää saman parin vastakkaiset suunnat. Säilytä alaviitteiden hakasulkeet osana huomautustekstiä.

Jaeteksti vastaa täsmälleen projektin lukittua lähdetietokantaa. Lähteen mahdolliset kursivoinnin tähdet ja runorivien `/`-merkit säilyvät tekstissä. Heprean ja kreikan sananselitykset ja lähdeviittaukset ovat alaviitteissä alkuperäisine kirjoitusmerkkeineen. Varsinaisia alkutekstiaineistoja tai lähdemoduuleja ei ole kopioitu tähän pakettiin.

## Toimitustiedot

AI-avusteisen laitoksen toimitustila on `unreviewed`. Tämä on olemassa olevan v005-laitoksen vienti; käännöksen sanamuotoa ei tarkistettu tai muutettu vientiä varten. Ristiviiteluettelo sisältää laitoksen nykyiset 55 paria. Se ei ole kattava tutkimusraamattujen ristiviitejärjestelmä.

Aineisto lisätään projektin omistajan pyynnöstä. Tämä vienti ei määritä uutta yleistä lisenssiä käännökselle eikä siirrä kolmansien osapuolten lähdeaineistojen oikeuksia. Sovelluskoodin lisenssi ja tämän tekstiaineiston oikeustiedot ovat erilliset.

Uudelleenluonti projektin E-aseman lähdeaineistosta:

```powershell
python tools/export-finnish-edition.py E:\FinnishTranslation-edition
```
