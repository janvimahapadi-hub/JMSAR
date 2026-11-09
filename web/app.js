"use strict";
const MONTHS=["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"];
const el=id=>document.getElementById(id);
const state={caseId:null,record:null,month:0,selectedClass:6,status:null,jobTimer:null,toastTimer:null};
const $=(tag,props={},children=[])=>{const x=document.createElement(tag);for(const [k,v] of Object.entries(props)){if(k==="className")x.className=v;else if(k==="text")x.textContent=v;else x.setAttribute(k,v)}children.forEach(c=>x.append(c));return x};
const fmt=(n,d=1)=>Number(n||0).toFixed(d);
const escapeText=str=>String(str??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const monthFull=i=>MONTHS[i]+" 2021";
const api=async(path,options)=>{const res=await fetch(path,{cache:"no-store",...options});const raw=await res.text();let data;try{data=JSON.parse(raw)}catch{data={detail:raw}}if(!res.ok)throw Error(typeof data.detail==="string"?data.detail:JSON.stringify(data.detail||data));return data};
const toast=(message)=>{const node=el("toast");node.textContent=message;node.classList.add("show");clearTimeout(state.toastTimer);state.toastTimer=setTimeout(()=>node.classList.remove("show"),5500)};
const canvasImage=(kind,m)=>state.caseId?"/api/cases/"+encodeURIComponent(state.caseId)+"/image/"+m+"/"+kind:"";
async function boot(){
  MONTHS.forEach((label,i)=>{const b=$("button",{type:"button",text:label,"aria-label":label+" 2021"});b.onclick=()=>changeMonth(i);el("month-pick").append(b)});
  el("blend").addEventListener("input",e=>setBlend(+e.target.value));
  el("new-location").onclick=()=>el("location-dialog").showModal();
  el("close-dialog").onclick=()=>el("location-dialog").close();
  el("location-form").addEventListener("submit",submitLocation);
  el("rail-about").onclick=()=>el("about-dialog").showModal();
  el("rail-method").onclick=()=>{el("about-dialog").showModal();};
  document.querySelectorAll(".info-close").forEach(b=>b.onclick=()=>el("about-dialog").close());
  el("download-record").onclick=download;
  setBlend(75);
  await refreshStatus();
  try {const cases=await api("/api/cases");if(!cases.length){toast("No 2021 saved cases found. Install the original SARScope core and verified model for new analyses.");return}
    const first=cases.find(c=>c.id==="mannheim")||cases[0];await loadCase(first.id)
  } catch(err){toast("Core is unavailable: "+err.message)}
}
async function refreshStatus(){
  const s=await api("/api/status");state.status=s;const node=el("status");
  node.className="status "+(s.ready_for_new_inference?"ok":s.core_online?"":"off");
  node.querySelector("span").textContent=s.ready_for_new_inference?"INFERENCE READY":s.core_online?"SAVED STUDY":"CORE OFFLINE";
}
async function loadCase(id){
  const data=await api("/api/cases/"+encodeURIComponent(id)+"/summary");
  if(data.spec.start_month!=="2021-01")throw Error("Only 2021 cases can be loaded");
  state.record=data;state.caseId=id;state.month=0;state.selectedClass=data.analysis.dominant_class_id;
  el("site-name").textContent=data.name;
  el("coordinates").textContent=fmt(data.spec.latitude,4)+"° · "+fmt(data.spec.longitude,4)+"° · 10 m / pixel";
  el("dominant-class").textContent=data.classes[state.selectedClass].name;
  const peak=data.analysis.largest_monthly_mix_shift;
  el("largest-shift").textContent=peak?fmt(peak.pp,2)+" pp":"—";
  el("shift-period").textContent=peak?peak.from+" → "+peak.to:"";
  changeMonth(0);renderSeries();renderQuality();
  toast("Loaded genuine 2021 saved model output · "+data.name);
}
function changeMonth(index){
  state.month=index;document.querySelectorAll("#month-pick button").forEach((b,i)=>{b.classList.toggle("active",i===index);b.setAttribute("aria-pressed",String(i===index))});
  el("map-month-label").textContent=monthFull(index);el("share-month").textContent=monthFull(index);
  if(!state.record)return;
  const m=state.record.months[index].month;
  el("map-foreground").style.backgroundImage="url('"+canvasImage("map",m)+"')";
  el("radar-background").style.backgroundImage=state.record.months[index].radar?"url('"+canvasImage("radar",m)+"')":"none";
  renderComposition();renderSeries();renderQuality();
}
function setBlend(n){el("blend-percent").textContent=n+"%";el("map-foreground").style.opacity=n/100;}
function renderComposition(){
  const target=el("composition");target.replaceChildren();
  if(!state.record)return;
  const items=state.record.months[state.month].shares.filter(s=>s.class_id>=0&&s.class_id<9).sort((a,b)=>b.percent-a.percent);
  const shown=items.filter(x=>x.percent>=.05).slice(0,7);
  for(const s of shown){
    const cls=state.record.classes.find(c=>c.id===s.class_id);
    const row=$("button",{className:"bar-row",type:"button",title:"Show "+cls.name+" through 2021"});
    row.style.cssText="background:transparent;border:0;text-align:left;color:inherit;padding:0;cursor:pointer";
    const group=$("div");
    const top=$("div",{className:"bar-top"},[$("span",{className:"swatch"}),$("span",{text:cls.name})]);
    top.firstChild.style.background=cls.color;
    const track=$("div",{className:"bar-track"},[$("div",{className:"bar-fill"})]);
    track.firstChild.style.width=fmt(s.percent,3)+"%";track.firstChild.style.background=cls.color;
    group.append(top,track);row.append(group,$("span",{className:"bar-percent",text:fmt(s.percent,1)+"%"}));
    row.onclick=()=>{state.selectedClass=cls.id;renderSeries()};target.append(row);
  }
  if(shown.length===0)target.append($("div",{className:"placeholder",text:"No scored class shares available."}));
}
function renderSeries(){
  if(!state.record)return;
  const cls=state.record.classes.find(c=>c.id===state.selectedClass);
  const values=state.record.months.map(m=>m.shares.find(s=>s.class_id===cls.id)?.percent||0);
  el("series-class").textContent=cls.name;el("series-value").textContent=fmt(values[state.month],2)+"%";
  const max=Math.max(2,...values)*1.13;
  const pts=values.map((v,i)=>[i*300/11,66-v/max*57]);
  const path=pts.map(([x,y],i)=>(i?"L":"M")+x.toFixed(2)+","+y.toFixed(2)).join(" ");
  const area=path+" L300,72 L0,72 Z";
  const active=pts[state.month];
  el("series").innerHTML='<svg viewBox="0 0 300 78" preserveAspectRatio="none" role="img" aria-label="'+escapeText(cls.name)+' monthly 2021 share chart">'+
    '<path d="M0 72 H300 M0 39 H300 M0 6 H300" stroke="#344249" stroke-width=".8" fill="none"/>'+
    '<path d="'+area+'" fill="'+cls.color+'" opacity=".12"/>'+
    '<path d="'+path+'" fill="none" stroke="'+cls.color+'" stroke-width="2.2" vector-effect="non-scaling-stroke"/>'+
    '<line x1="'+active[0]+'" x2="'+active[0]+'" y1="3" y2="73" stroke="#d9c7a0" stroke-dasharray="3 4" opacity=".5"/>'+
    '<circle cx="'+active[0]+'" cy="'+active[1]+'" r="4" fill="#f3e6c8" stroke="'+cls.color+'" stroke-width="2"/></svg>'+
    '<div class="axis-labels"><span>JAN</span><span>APR</span><span>JUL</span><span>OCT</span><span>DEC</span></div>';
}
function renderQuality(){
  if(!state.record)return;
  const m=state.record.months[state.month];
  const warnings=m.quality?.warnings;
  let note="Prediction map from SARScope. The 2021 model's held-out weak-label accuracy is not an independent accuracy guarantee at this location.";
  if(Array.isArray(warnings)&&warnings.length)note=warnings.map(w=>typeof w==="string"?w:JSON.stringify(w)).slice(0,2).join(" · ");
  else if(m.coverage!==undefined)note="Model-labelled coverage: "+fmt(m.coverage,1)+"%. Coverage is not a measure of correctness. Review radar support and compare with independent reference data.";
  el("quality-note").textContent=note;
}
function download(){
  if(!state.record){toast("Load a case before exporting.");return}
  const list=state.record.exports||[];
  const file=list.includes("case_export.zip")?"case_export.zip":list.includes("monthly_shares.csv")?"monthly_shares.csv":null;
  if(!file){toast("No saved case export available.");return}
  const a=document.createElement("a");
  a.href="/api/cases/"+encodeURIComponent(state.caseId)+"/export/"+encodeURIComponent(file);a.download=file;a.click();
}
async function submitLocation(event){
  event.preventDefault();
  const payload={latitude:+el("latitude").value,longitude:+el("longitude").value,project:el("project").value.trim()};
  const place=el("job-status");place.textContent="Validating a new 2021 request…";
  try {
    const r=await api("/api/analyze",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(payload)});
    place.textContent="Job accepted. Retrieving 12 months and processing with the verified model…";
    el("location-form").querySelector(".primary").disabled=true;
    if(state.jobTimer)clearInterval(state.jobTimer);
    let busy=false;
    state.jobTimer=setInterval(async()=>{
      if(busy)return;busy=true;
      try{
        const job=await api("/api/jobs/"+encodeURIComponent(r.job_id));
        place.textContent=(job.messages||[]).slice(-3).join("\n")||job.state;
        if(job.state==="complete"||job.state==="failed"){
          clearInterval(state.jobTimer);state.jobTimer=null;
          el("location-form").querySelector(".primary").disabled=false;
          if(job.state==="failed"){toast("Analysis failed: "+(job.error||"Check the core worker log"));return}
          await loadCase(job.case_id);await refreshStatus();
          el("location-dialog").close();toast("2021 analysis complete. Outputs are ready to inspect.");
        }
      }catch(err){clearInterval(state.jobTimer);state.jobTimer=null;el("location-form").querySelector(".primary").disabled=false;place.textContent=err.message}
      finally{busy=false}
    },2800);
  }catch(err){place.textContent="Cannot begin analysis: "+err.message;toast("New inference requires the verified checkpoint, CPU dependencies and Earth Engine authentication.")}
}
boot().catch(err=>toast("Startup error: "+err.message));
