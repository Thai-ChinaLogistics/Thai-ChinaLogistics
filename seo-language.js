(()=>{
  const allowed=['zh','en','th'];
  const normalize=(v)=>{v=String(v||'').toLowerCase();if(v.startsWith('th'))return'th';if(v.startsWith('en'))return'en';if(v.startsWith('zh'))return'zh';return''};
  const params=new URLSearchParams(location.search);
  const forced=normalize(params.get('lang'));
  let saved='';
  try{saved=normalize(localStorage.getItem('siteLanguage')||localStorage.getItem('siteLang')||localStorage.getItem('tcl_seo_lang'));}catch(e){}
  const browser=normalize((navigator.languages&&navigator.languages[0])||navigator.language||'');
  const ref=String(document.referrer||'').toLowerCase();
  const refHint=!saved&&!browser&&(ref.includes('google.co.th')?'th':(ref.includes('google.com')?'en':''));
  let lang=forced||saved||browser||refHint||'zh';
  if(!allowed.includes(lang))lang='zh';
  const meta=window.TCL_SEO_PAGE_META||{};
  const applyMeta=(l)=>{const m=meta[l]||meta.zh;if(!m)return;document.documentElement.lang=m.lang||({'zh':'zh-CN','en':'en','th':'th'}[l]);document.title=m.title||document.title;const d=document.querySelector('meta[name="description"]');if(d&&m.description)d.content=m.description;const ot=document.querySelector('meta[property="og:title"]');if(ot&&m.title)ot.content=m.title;const od=document.querySelector('meta[property="og:description"]');if(od&&m.description)od.content=m.description;};
  document.documentElement.dataset.lang=lang;applyMeta(lang);
  const persist=(l)=>{try{localStorage.setItem('tcl_seo_lang',l);localStorage.setItem('siteLanguage',l);localStorage.setItem('siteLang',l);}catch(e){}};
  const apply=(l,persistChoice=true)=>{l=normalize(l)||'zh';document.documentElement.dataset.lang=l;applyMeta(l);document.querySelectorAll('button[data-lang]').forEach(b=>{const on=b.dataset.lang===l;b.classList.toggle('active',on);b.setAttribute('aria-pressed',on?'true':'false')});if(persistChoice)persist(l);};
  const ready=()=>{document.querySelectorAll('button[data-lang]').forEach(btn=>btn.addEventListener('click',()=>apply(btn.dataset.lang,true)));apply(lang,false);};
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',ready,{once:true});else ready();
})();
