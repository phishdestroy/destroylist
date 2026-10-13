'use strict';
(()=>{
  const scene=document.getElementById('globe-scene');
  const canvas=document.getElementById('defense-globe');
  if(!scene||!canvas)return;
  const ctx=canvas.getContext('2d',{alpha:true});
  if(!ctx)return;
  // A conceptual network, not a map of observed attacks or live telemetry.
  const golden=Math.PI*(3-Math.sqrt(5));
  const points=Array.from({length:1050},(_,i)=>{
    const y=1-2*(i+.5)/1050,r=Math.sqrt(1-y*y),a=i*golden;
    return {x:r*Math.cos(a),y,z:r*Math.sin(a),highlight:i%79===0};
  });
  let frame=0,last=0,rotation=.28,visible=true,enabled=document.documentElement.dataset.motion==='on';
  let pointerX=0,pointerY=0,tiltX=0,tiltY=0,clock=0;
  function project(x,y,z){
    const a=rotation+tiltX, ca=Math.cos(a),sa=Math.sin(a);
    const xr=x*ca-z*sa,zr=x*sa+z*ca;
    const t=-.23+tiltY,ct=Math.cos(t),st=Math.sin(t);
    const yr=y*ct-zr*st,zz=y*st+zr*ct;
    return {x:320+xr*226,y:320+yr*226,z:zz};
  }
  function resize(){
    const dpr=Math.min(window.devicePixelRatio||1,1.75);
    const size=Math.max(1,Math.round(canvas.getBoundingClientRect().width*dpr));
    canvas.width=size;canvas.height=size;ctx.setTransform(size/640,0,0,size/640,0,0);draw();
  }
  function gridLine(latitude,longitude){
    let previous;
    for(let i=0;i<=72;i++){
      const a=i/72*Math.PI*2;
      const p=latitude===null?project(Math.cos(longitude)*Math.sin(a),Math.cos(a),Math.sin(longitude)*Math.sin(a)):project(Math.cos(latitude)*Math.cos(a),Math.sin(latitude),Math.cos(latitude)*Math.sin(a));
      if(previous){ctx.beginPath();ctx.moveTo(previous.x,previous.y);ctx.lineTo(p.x,p.y);ctx.strokeStyle=`rgba(141,195,155,${.017+(p.z+1)*.025})`;ctx.lineWidth=.65;ctx.stroke();}previous=p;
    }
  }
  function draw(){
    ctx.clearRect(0,0,640,640);
    for(let lat=-Math.PI/3;lat<=Math.PI/3;lat+=Math.PI/6)gridLine(lat,0);
    for(let lng=0;lng<Math.PI;lng+=Math.PI/5)gridLine(null,lng);
    for(const point of points){
      const p=project(point.x,point.y,point.z);
      const front=(p.z+1)/2;
      const band=Math.max(0,1-Math.abs(p.y-(170+(clock*.018%300)))/34);
      const alpha=.1+front*.56+band*.19;
      ctx.beginPath();ctx.arc(p.x,p.y,point.highlight?1.7: .65+front*.7,0,Math.PI*2);
      ctx.fillStyle=point.highlight?`rgba(219,242,168,${alpha})`:`rgba(151,211,174,${alpha})`;ctx.fill();
      if(point.highlight&&p.z>.25){ctx.beginPath();ctx.arc(p.x,p.y,4,0,Math.PI*2);ctx.strokeStyle=`rgba(205,235,159,${front*.2})`;ctx.lineWidth=.7;ctx.stroke();}
    }
    ctx.beginPath();ctx.arc(320,320,228,0,Math.PI*2);ctx.strokeStyle='rgba(180,223,156,.13)';ctx.lineWidth=.7;ctx.stroke();
  }
  function tick(now){
    frame=0;
    if(!enabled||!visible||document.hidden)return;
    if(now-last>=32){const dt=Math.min(now-last,60);last=now;clock+=dt;rotation+=dt*.000042;tiltX+=(pointerX-tiltX)*.055;tiltY+=(pointerY-tiltY)*.055;draw();}
    frame=requestAnimationFrame(tick);
  }
  function sync(){
    enabled=document.documentElement.dataset.motion==='on';
    if(frame){cancelAnimationFrame(frame);frame=0;}
    if(enabled&&visible&&!document.hidden){last=performance.now();frame=requestAnimationFrame(tick);}else draw();
  }
  scene.addEventListener('pointermove',event=>{if(event.pointerType==='touch'||!enabled)return;const box=scene.getBoundingClientRect();pointerX=((event.clientX-box.left)/box.width-.5)*.35;pointerY=((event.clientY-box.top)/box.height-.5)*.2;},{passive:true});
  scene.addEventListener('pointerleave',()=>{pointerX=0;pointerY=0;});
  new MutationObserver(sync).observe(document.documentElement,{attributes:true,attributeFilter:['data-motion']});
  if('IntersectionObserver'in window)new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;sync();},{rootMargin:'80px'}).observe(scene);
  if('ResizeObserver'in window)new ResizeObserver(resize).observe(scene);else window.addEventListener('resize',resize,{passive:true});
  document.addEventListener('visibilitychange',sync);
  resize();scene.classList.add('canvas-ready');sync();
})();