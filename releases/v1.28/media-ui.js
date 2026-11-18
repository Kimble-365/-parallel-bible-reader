'use strict';
(()=>{
 const $=id=>document.getElementById(id),data=window.ReaderMediaResources,films=data.films,control=$('film-language'),catalog=window.BibleCatalog;
 function meta(){return catalog.editions.find(e=>e.id===$('primary').value)}
 function matching(){const language=meta()?.language?.split('-')[0];return films.find(f=>f.language_tags.includes(language))}
 let preferred;try{preferred=localStorage.getItem('bible-reader-film-v1')}catch{}
 for(const film of films){const option=document.createElement('option');option.value=film.id;option.textContent=film.label;control.append(option)}
 control.value=films.some(f=>f.id===preferred)?preferred:matching()?.id||'eng';
 function refresh(){const film=films.find(f=>f.id===control.value);$('film-watch').href=film.url;$('film-watch').textContent='Watch JESUS — '+film.label;$('film-description').textContent='Opens the official Jesus Film Project player in a new tab. Choose the spoken language or a regional variant there if needed. Internet is required; the film is not part of saved Bible texts.';const match=matching();$('film-match').disabled=!match;$('film-match').textContent=match?'Use Text 1 language — '+match.label:'No film language shortcut for Text 1';$('film-more').href=data.more_languages;
  const links=$('provider-links');links.replaceChildren();const seen=new Set();for(const slot of ['primary','compare1','compare2','compare3']){const e=catalog.editions.find(e=>e.id===$(slot).value);for(const link of e?.provider_links||[]){if(seen.has(link.url))continue;seen.add(link.url);const li=document.createElement('li'),a=document.createElement('a');a.textContent=e.label+' · '+link.label;a.href=link.url;a.target='_blank';a.rel='noopener noreferrer';li.append(a);links.append(li)}}$('provider-empty').hidden=seen.size>0;
 }
 control.onchange=()=>{try{localStorage.setItem('bible-reader-film-v1',control.value)}catch{}refresh()};$('film-match').onclick=()=>{const match=matching();if(match){control.value=match.id;control.onchange()}};for(const id of ['primary','compare1','compare2','compare3'])$(id).addEventListener('change',refresh);refresh();
})();
