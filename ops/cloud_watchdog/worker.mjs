// Deployment proposal only. No credentials are embedded in this source.
const API='https://api.github.com/repos/jsdwxdzy-lab/research-radar';
const PUBLIC='https://jsdwxdzy-lab.github.io/research-radar/';
const RAW='https://raw.githubusercontent.com/jsdwxdzy-lab/research-radar/main/index.html';

export function shanghaiDay(now){return new Date(now+8*3600000).toISOString().slice(0,10)}
export function parseBoard(html){
    const match=html.match(/^(?:const|let) DATA\s*=\s*(\{[^\n]*\});?\s*$/m);
    if(!match)throw Error('board-data-missing');
    return JSON.parse(match[1]);
}
export function fresh(data,today){
    return !!(data&&data.today===today&&data.run?.status==='ok'&&String(data.run.started).startsWith(today+'T')&&
        data.health?.length&&data.health.every(h=>!h.err)&&data.items?.length&&
        data.items.every(i=>String(i.tz||'').trim()&&(!String(i.a||'').trim()||String(i.az||'').trim())));
}
export function decide({now,publicBoard,repositoryBoard,dailyRuns=[],pagesRuns=[]}){
    const today=shanghaiDay(now);
    if(fresh(publicBoard,today))return {action:'none',reason:'public-board-current'};
    const latest=list=>[...list].sort((a,b)=>Date.parse(b.created_at)-Date.parse(a.created_at))[0];
    const active=[...dailyRuns,...pagesRuns].filter(r=>r.status!=='completed');
    if(active.length)return {action:'wait',reason:active.some(r=>now-Date.parse(r.created_at)>110*60000)?'attention-long-running-job':'job-in-progress'};
    const kind=fresh(repositoryBoard,today)?'pages':'daily';
    const previous=latest(kind==='pages'?pagesRuns:dailyRuns);
    const cooldown=(kind==='pages'?10:45)*60000;
    if(previous&&now-Date.parse(previous.created_at)<cooldown)return {action:'wait',reason:'retry-cooldown'};
    return {action:kind,reason:kind==='pages'?'publication-stale':'fetch-or-translation-stale'};
}
export async function check(env,now=Date.now(),fetcher=fetch){
    if(!env.RADAR_GITHUB_TOKEN)throw Error('missing-RADAR_GITHUB_TOKEN');
    async function get(url,authenticated=false){
        const response=await fetcher(url,{headers:{'User-Agent':'research-radar-watchdog',...(authenticated?{
            'Authorization':'Bearer '+env.RADAR_GITHUB_TOKEN,'Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'
        }:{'Cache-Control':'no-cache'})},signal:AbortSignal.timeout(15000)});
        if(!response.ok)throw Error('read-http-'+response.status);
        return authenticated?response.json():response.text();
    }
    let publicBoard=null;
    try{publicBoard=parseBoard(await get(PUBLIC+'?watchdog='+Math.floor(now/60000)))}catch{}
    if(fresh(publicBoard,shanghaiDay(now)))return {action:'none',reason:'public-board-current'};
    // Fail closed if GitHub cannot be inspected; never repeatedly dispatch blindly.
    const [daily,pages]=await Promise.all([
        get(API+'/actions/workflows/daily.yml/runs?per_page=20',true),
        get(API+'/actions/workflows/pages.yml/runs?per_page=20',true)
    ]);
    let repositoryBoard=null;
    try{repositoryBoard=parseBoard(await get(RAW+'?watchdog='+Math.floor(now/60000)))}catch{}
    const result=decide({now,publicBoard,repositoryBoard,dailyRuns:daily.workflow_runs,pagesRuns:pages.workflow_runs});
    if(result.action==='daily'||result.action==='pages'){
        const response=await fetcher(API+'/actions/workflows/'+result.action+'.yml/dispatches',{
            method:'POST',headers:{'Authorization':'Bearer '+env.RADAR_GITHUB_TOKEN,'User-Agent':'research-radar-watchdog',
                'Accept':'application/vnd.github+json','Content-Type':'application/json','X-GitHub-Api-Version':'2022-11-28'},
            body:JSON.stringify({ref:'main'}),signal:AbortSignal.timeout(15000)
        });
        if(response.status!==204)throw Error('dispatch-http-'+response.status);
    }
    return result;
}
export default {
    // No public HTTP endpoint may dispatch jobs.
    fetch(){return new Response('Not found',{status:404})},
    async scheduled(event,env){
        try{const result=await check(env,event.scheduledTime);console.log(JSON.stringify({date:shanghaiDay(event.scheduledTime),...result}));
            if(result.reason==='attention-long-running-job')throw Error('attention-long-running-job');
        }catch{console.error('radar-watchdog-check-failed');throw Error('radar-watchdog-check-failed')}
    }
};
