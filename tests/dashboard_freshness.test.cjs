const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const html=fs.readFileSync(__dirname+'/../radar/web/dashboard.html','utf8');
const source=html.split('// BEGIN freshness checks')[1].split('\n').slice(1).join('\n').split('// END freshness checks.')[0];
function context({server,hidden=false,editing=false}={}){
    const calls=[],listeners={},nodes={};let reloaded=0,renders=0;
    const status={after(n){nodes['#'+n.id]=n}};
    function node(){return {children:[],setAttribute(){},replaceChildren(){this.children=[]},append(...ns){this.children.push(...ns)},addEventListener(t,f){this[t]=f}}}
    const state={console,URL,AbortSignal,setInterval(){},Date,DATA:{generated:'2026-10-28 21:31'},
        TODAY:'2026-10-28',shanghaiDay:()=> '2026-10-29',document:{hidden,activeElement:{tagName:editing?'TEXTAREA':'BODY'},createElement:node,addEventListener(t,f){listeners[t]=f}},
        window:{addEventListener(t,f){listeners[t]=f}},location:{href:'https://jsdwxdzy-lab.github.io/research-radar/#',reload(){reloaded++}},
        $:id=>id==='#status'?status:nodes[id],header(){},trends(){},render(){renders++},save(){},
        fetch:async(url,options)=>{calls.push({url:String(url),options});return {ok:true,text:async()=>server||'invalid'}}};
    vm.createContext(state);vm.runInContext(source,state);
    return {state,calls,nodes,listeners,reloaded:()=>reloaded,renders:()=>renders};
}
test('crossing midnight refreshes the real calendar',()=>{const c=context();assert.equal(c.state.TODAY,'2026-10-29');assert.equal(c.renders(),1)});
test('midnight does not replace an actively edited note',()=>{const c=context({editing:true});assert.equal(c.renders(),0);assert.equal(c.state.TODAY,'2026-10-28')});
test('hidden tabs make no requests',()=>{const c=context({hidden:true});assert.equal(c.calls.length,0)});
test('new data prompts a user-controlled reload instead of replacing reading work',async()=>{
    const c=context({server:'const DATA = '+JSON.stringify({generated:'2026-10-29 10:44',items:[]})+';'});
    await new Promise(resolve=>setImmediate(resolve));
    assert.equal(c.reloaded(),0);assert(c.nodes['#freshnessNotice']);assert.equal(c.calls[0].options.credentials,'omit');
    assert.equal(c.calls[0].options.cache,'no-store');c.nodes['#freshnessNotice'].children[1].click();assert.equal(c.reloaded(),1);
});
test('invalid response is never evaluated as code',async()=>{const c=context({server:'throw new Error("DO NOT EXECUTE")'});await new Promise(resolve=>setImmediate(resolve));assert.equal(c.nodes['#freshnessNotice'],undefined)});
test('focus and visibility handlers are installed',()=>{const c=context();assert.equal(typeof c.listeners.focus,'function');assert.equal(typeof c.listeners.visibilitychange,'function');assert.equal(typeof c.listeners.pageshow,'function')});
