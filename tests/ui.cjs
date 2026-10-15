// Exercise the actual inline UI script using a minimal DOM and HTTP responses.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const path=require('node:path');
const html=fs.readFileSync(path.join(__dirname,'../02_Firmware/relay_web/web_ui.h'),'utf8');
const elements=new Map();
const element=id=>{if(!elements.has(id))elements.set(id,{textContent:'',disabled:true,innerHTML:'',classList:{toggle(){}},append(){}});return elements.get(id);};
let state={version:'0.1.0',buildUTC:'2026-10-15T00:00:00Z',ready:true,mask:0,error:'',staConnected:true,staIP:'192.0.2.2',apIP:'192.168.4.1',apName:'JIN-Relay-TEST'},calls=[],offline=false;
const context=vm.createContext({document:{getElementById:element,createElement:()=>({classList:{toggle(){}},append(){}})},URLSearchParams,AbortSignal,setInterval(){},fetch:async(url,opt)=>{calls.push([url,opt]);if(offline)throw Error('offline');if(opt.method==='POST'){const p=opt.body;if(url==='/api/all')state.mask=p.get('state')==='1'?255:0;else{const bit=1<<(Number(p.get('channel'))-1);state.mask=p.get('state')==='1'?state.mask|bit:state.mask&~bit;}}return{ok:true,json:async()=>({...state})};}});
vm.runInContext(html.match(/<script>([\s\S]*?)<\/script>/)[1],context);
const flush=()=>new Promise(resolve=>setImmediate(resolve));
(async()=>{
await flush();assert.match(element('identity').textContent,/0.1.0.*Build UTC/);
for(let ch=1;ch<=8;ch++){await element('relay'+ch).onclick();assert.equal(state.mask,(1<<ch)-1);assert.equal(element('state'+ch).textContent,'ON');}
assert.equal(state.mask,255);await element('allOff').onclick();assert.equal(state.mask,0);
await element('allOn').onclick();assert.equal(state.mask,255);
await element('relay8').onclick();assert.equal(state.mask,127);
state.ready=false;state.mask=null;state.error='I2C fault';await vm.runInContext('poll()',context);
assert.equal(element('state1').textContent,'UNKNOWN');assert.equal(element('relay1').disabled,true);assert.equal(element('allOn').disabled,true);
const before=calls.length;await element('relay1').onclick();assert.equal(calls.length,before);
offline=true;await vm.runInContext('poll()',context);assert.equal(element('connection').textContent,'Terputus');assert.equal(element('allOff').disabled,true);
offline=false;state.ready=true;state.mask=0;await vm.runInContext('poll()',context);assert.equal(element('relay1').disabled,false);
console.log('UI PASS: channels 1-8, bit isolation, all ON/OFF, fault lock, disconnect, recovery, identity. Simulated DOM/HTTP only.');
})().catch(e=>{console.error(e);process.exitCode=1;});
