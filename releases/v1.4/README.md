# Reader 1.4 — experimental Urdu written-script adapters

Adds independent written-script choices for each Urdu slot: source, Devanagari or Perso-Arabic. Both existing Urdu editions retain their own source and license; they are not presented as the same translation. The same edition can occupy two slots with different script choices. Share links and reading state preserve the per-slot forms.

The transparent project mapping is explicitly lossy and experimental. Perso-Arabic consonants without written vowels keep a Devanagari virama rather than inventing a vowel. Some Arabic distinctions merge; waw/yeh/ain and vowel carriers are intrinsically ambiguous. The result is an orthographic reading aid, not natural Devanagari Urdu or a pronunciation guide. Source text is never modified. The source's existing Latin conversion remains available under Reading appearance.

A universal adapter interface reports method/version, target script, direction and unresolved letters. Only the two supported Urdu editions expose these options. Other languages do not receive guessed conversions.
