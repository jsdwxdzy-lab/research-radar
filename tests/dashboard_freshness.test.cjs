const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const html=fs.readFileSync(__dirname+'/../radar/web/dashboard.html','utf8');
const source=html.split('// BEGIN freshness checks')[1].split('\n').slice(1).join('\n').split('// END freshness checks.')[0]
  .replace(/\ncheckForUpdates\(\);\s*$/,'\n');
function context({board,hidden=false,editing=false,synced=false}={}){
    const calls=[],listeners={},nodes={};let renders=0;
    const status={after(n){nodes['#'+n.id]=n}};
    function node(){return {id:'',textContent:'',children:[],className:'',setAttribute(){},replaceChildren(){this.children=[]},append(...ns){this.children.push(...ns)},addEventListener(t,f){this[t]=f}}}
    const state={console,URL,AbortSignal,setInterval(){},Date,JSON,
        DATA:{generated:'2026-10-28 21:31',items:[]},SYNC_BASE:'',syncLoggedIn:synced,
        TODAY:'2026-10-28',shanghaiDay:()=> '2026-10-29',document:{hidden,activeElement:{tagName:editing?'TEXTAREA':'BODY'},createElement:node,addEventListener(t,f){listeners[t]=f}},
        window:{addEventListener(t,f){listeners[t]=f}},location:{href:'https://jsdwxdzy-lab.github.io/research-radar/#'},
        $:id=>id==='#status'?status:nodes[id],header(){},trends(){},render(){renders++},defaultBrowseState(){},syncPull(){},
        fetch:async(url,options)=>{calls.push({url:String(url),options});return {ok:true,json:async()=>board||{}} }};
    state.adoptBoard=function(next){if(!next||!Array.isArray(next.items))return false;state.DATA=next;return true};
    vm.createContext(state);vm.runInContext(source,state);
    return {state,calls,nodes,listeners,renders:()=>renders};
}
test('crossing midnight refreshes the real calendar',()=>{const c=context();c.state.refreshCalendar();assert.equal(c.state.TODAY,'2026-10-29');assert.equal(c.renders(),1)});
test('midnight does not replace an actively edited note',()=>{const c=context({editing:true});c.state.refreshCalendar();assert.equal(c.renders(),0);assert.equal(c.state.TODAY,'2026-10-28')});
test('hidden tabs make no requests',async()=>{const c=context({hidden:true});await c.state.checkForUpdates(true);assert.equal(c.calls.length,0)});
test('newer data.json is adopted without a full reload',async()=>{
    const c=context({board:{generated:'2026-10-29 10:44',items:[{k:'a'}]}});
    await c.state.checkForUpdates(true);
    assert.equal(c.state.DATA.generated,'2026-10-29 10:44');
    assert(String(c.calls[0].url).includes('data.json'));
    assert.equal(c.calls[0].options.credentials,'omit');
    assert.equal(c.calls[0].options.cache,'no-store');
    assert(c.nodes['#freshnessNotice']);
});
test('invalid response is never evaluated as code',async()=>{
    const c=context();
    c.state.fetch=async()=>({ok:true,json:async()=>{throw new Error('DO NOT EXECUTE')}});
    await c.state.checkForUpdates(true);
    assert.equal(c.nodes['#freshnessNotice'],undefined);
});
test('focus and visibility handlers are installed',()=>{const c=context();assert.equal(typeof c.listeners.focus,'function');assert.equal(typeof c.listeners.visibilitychange,'function');assert.equal(typeof c.listeners.pageshow,'function')});
