// Progressive enhancement: the generated page contains every card and link.
function makeDirectory({cards,search,filters,count,empty,more,reset,controls,limit,noun,matches,filterKey}){
  let selected='all',expanded=false;
  const query=()=>search.value.trim().toLowerCase();
  function render(){
    const term=query();const matched=cards.filter(card=>(selected==='all'||matches(card,selected))&&card.dataset[filterKey].includes(term));
    const filtered=Boolean(term)||selected!=='all';
    const visible=expanded||filtered?matched:matched.slice(0,limit);
    const shown=new Set(visible);cards.forEach(card=>card.hidden=!shown.has(card));
    count.textContent=matched.length?'Showing '+visible.length+' of '+matched.length+(filtered?' matching ':' ')+noun+' · A–Z':'No matching '+noun;
    empty.hidden=matched.length>0;
    reset.hidden=!filtered;
    controls.hidden=filtered||matched.length<=limit;
    more.textContent=expanded?'Show fewer '+noun+' ↑':'Show all '+matched.length+' '+noun+' ↓';
    more.setAttribute('aria-expanded',String(expanded));
    filters.forEach(button=>button.setAttribute('aria-pressed',String(button.dataset[filterKey==='search'?'filter':'toolFilter']===selected)));
    return visible;
  }
  function choose(value){selected=value;expanded=false;render();}
  filters.forEach(button=>button.addEventListener('click',()=>choose(button.dataset[filterKey==='search'?'filter':'toolFilter'])));
  search.addEventListener('input',()=>{expanded=false;render();});
  reset.addEventListener('click',()=>{search.value='';selected='all';expanded=false;render();search.focus();});
  more.addEventListener('click',()=>{
    const firstNew=cards.filter(card=>card.hidden)[0];expanded=!expanded;render();
    if(expanded&&firstNew){firstNew.querySelector('a')?.focus({preventScroll:true});firstNew.scrollIntoView({block:'nearest',behavior:motionOn?'smooth':'auto'});}
    else{more.focus({preventScroll:true});more.scrollIntoView({block:'nearest',behavior:motionOn?'smooth':'auto'});}
  });
  render();
  return {choose(value){search.value='';choose(value);},reveal(){search.value='';selected='all';expanded=true;render();}};
}
const sourceDirectory=makeDirectory({cards:all('.source'),search:$('source-search'),filters:all('[data-filter]'),count:$('source-count'),empty:$('source-empty'),more:$('show-sources'),reset:$('reset-sources'),controls:$('source-pagination'),limit:9,noun:'projects',matches:(card,value)=>card.dataset.category===value,filterKey:'search'});
const toolDirectory=makeDirectory({cards:all('.community-tool'),search:$('tool-search'),filters:all('[data-tool-filter]'),count:$('tool-count'),empty:$('tool-empty'),more:$('show-tools'),reset:$('reset-tools'),controls:$('tool-pagination'),limit:6,noun:'services',matches:(card,value)=>card.dataset.toolTasks.split(' ').includes(value),filterKey:'toolSearch'});
all('[data-tool-route]').forEach(link=>link.addEventListener('click',()=>toolDirectory.choose(link.dataset.toolRoute)));

function revealAnchor(hash,scroll=false){
  let id;try{id=decodeURIComponent(hash.slice(1));}catch{return;}
  const target=$(id);if(!target)return;
  const tool=target.closest('.community-tool');const source=target.closest('.source');
  if(tool?.hidden)toolDirectory.reveal();if(source?.hidden)sourceDirectory.reveal();
  for(let parent=target;parent;parent=parent.parentElement)if(parent.tagName==='DETAILS')parent.open=true;
  if(scroll)requestAnimationFrame(()=>target.scrollIntoView({block:'start',behavior:'auto'}));
}
document.addEventListener('click',event=>{const link=event.target.closest?.('a[href^="#"]');if(link)revealAnchor(link.getAttribute('href'));});
window.addEventListener('hashchange',()=>revealAnchor(location.hash,true));
if(location.hash)revealAnchor(location.hash,true);

const navLinks=all('#navigation a[href^="#"]');
const navSections=navLinks.map(link=>({link,section:$(link.hash.slice(1))})).filter(item=>item.section);
let navFrame=0;
function updateWayfinding(){
  navFrame=0;const boundary=document.querySelector('header').offsetHeight+150;
  const active=navSections.filter(item=>{const rect=item.section.getBoundingClientRect();return rect.top<=boundary&&rect.bottom>boundary;}).at(-1);
  navSections.forEach(item=>{if(item===active)item.link.setAttribute('aria-current','location');else item.link.removeAttribute('aria-current');});
  $('back-to-top').hidden=window.scrollY<800;
}
window.addEventListener('scroll',()=>{if(!navFrame)navFrame=requestAnimationFrame(updateWayfinding);},{passive:true});
window.addEventListener('resize',()=>{if(!navFrame)navFrame=requestAnimationFrame(updateWayfinding);},{passive:true});
updateWayfinding();