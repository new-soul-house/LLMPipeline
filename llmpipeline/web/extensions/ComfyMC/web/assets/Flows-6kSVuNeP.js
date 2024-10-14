import{A as Fe,F as Ce,_ as $e,a as be,b as ke,c as De,d as Se,e as ze}from"./ContextMenuTrigger.vue_vue_type_script_setup_true_lang-BRUDrEm3.js";import{T as Te,a as Y,_ as Be,t as ee,o as te,s as H,u as oe,F as j,b as L,c as U,d as ne,e as se,f as ae,g as Me}from"./RenameDialog.vue_vue_type_script_setup_true_lang-BqU9D-5A.js";import{o as a,a as v,g as m,d as $,h as P,i as y,w as t,j as X,m as z,u as o,e as G,k as Ie,l as le,p as D,c as e,q as W,n as Pe,s as ce,t as q,b as x,v as V,F as I,x as re,y as Re,z as Ae,r as ie,A as Oe,B as je,L as Le,I as E,C as ue,D as N,V as Ue,O as qe,H as Ee,E as Ne,_ as Ve,G as He,J as Ge,K as Ze}from"./index-Duqd1f_9.js";import{u as Ke,a as M,F as _e,b as Q,_ as de,c as pe,d as me,e as fe}from"./Input.vue_vue_type_script_setup_true_lang-BI8tpA8x.js";import{R as Je}from"./route-B9Whvd7H.js";import{_ as We,a as Qe,b as Xe,c as Ye,d as et,e as tt,f as ot}from"./PopoverTrigger.vue_vue_type_script_setup_true_lang-Cgr8Bu6q.js";import{c as Z,_ as K}from"./createLucideIcon-dytpvnWD.js";import{d as nt,v as st,_ as at}from"./defaultGraph-BoGYRZik.js";/**
 * @license lucide-vue-next v0.341.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const lt=Z("ArrowRightIcon",[["path",{d:"M5 12h14",key:"1ays0h"}],["path",{d:"m12 5 7 7-7 7",key:"xquz4c"}]]);/**
 * @license lucide-vue-next v0.341.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const ct=Z("FileUpIcon",[["path",{d:"M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z",key:"1rqfz7"}],["path",{d:"M14 2v4a2 2 0 0 0 2 2h4",key:"tnqrlb"}],["path",{d:"M12 12v6",key:"3ahymv"}],["path",{d:"m15 15-3-3-3 3",key:"15xj92"}]]);/**
 * @license lucide-vue-next v0.341.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const rt=Z("FolderPlusIcon",[["path",{d:"M12 10v6",key:"1bos4e"}],["path",{d:"M9 13h6",key:"1uhe8q"}],["path",{d:"M20 20a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.9a2 2 0 0 1-1.69-.9L9.6 3.9A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z",key:"1kt360"}]]);/**
 * @license lucide-vue-next v0.341.0 - ISC
 *
 * This source code is licensed under the ISC license.
 * See the LICENSE file in the root directory of this source tree.
 */const it=Z("PlusIcon",[["path",{d:"M5 12h14",key:"1ays0h"}],["path",{d:"M12 5v14",key:"s699le"}]]);function ut(_,n){return a(),v("svg",{width:"15",height:"15",viewBox:"0 0 15 15",fill:"none",xmlns:"http://www.w3.org/2000/svg"},[m("path",{"fill-rule":"evenodd","clip-rule":"evenodd",d:"M10 6.5C10 8.433 8.433 10 6.5 10C4.567 10 3 8.433 3 6.5C3 4.567 4.567 3 6.5 3C8.433 3 10 4.567 10 6.5ZM9.30884 10.0159C8.53901 10.6318 7.56251 11 6.5 11C4.01472 11 2 8.98528 2 6.5C2 4.01472 4.01472 2 6.5 2C8.98528 2 11 4.01472 11 6.5C11 7.56251 10.6318 8.53901 10.0159 9.30884L12.8536 12.1464C13.0488 12.3417 13.0488 12.6583 12.8536 12.8536C12.6583 13.0488 12.3417 13.0488 12.1464 12.8536L9.30884 10.0159Z",fill:"currentColor"})])}const _t=$({__name:"Label",props:{for:{},asChild:{type:Boolean},as:{},class:{}},setup(_){const n=_,c=P(()=>{const{class:l,...s}=n;return s});return(l,s)=>(a(),y(o(Ie),z(c.value,{class:o(G)("text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70",n.class)}),{default:t(()=>[X(l.$slots,"default")]),_:3},16,["class"]))}}),dt=["src"],pt={class:"w-full h-full bg-zinc-900 flex items-center justify-center"},mt={class:"flex flex-col gap-1"},ft={class:"flex font-medium text-sm opacity-80 select-none"},ht={class:"flex text-xs opacity-30 select-none"},wt=$({__name:"FlowsItem",props:{flow:{},selected:{type:Boolean}},emits:["onSelect"],setup(_,{emit:n}){const c=_,l=n,s=P(()=>c.flow.thumbnail),f=le();function i(){f.push({name:"Flow",params:{id:c.flow.id}})}const{shift:p}=Ke();function h(){p.value?l("onSelect"):i()}const r=D(!1);function w(){M("Flows::Refresh").emit()}const d=D(!1);function C(){M("Flows::Refresh").emit()}return(b,g)=>{const T=$e,k=be,F=ke,R=De,A=Se,O=Be,B=ze;return a(),v(I,null,[e(A,{onContextmenu:g[2]||(g[2]=W(()=>{},["prevent"]))},{default:t(()=>[e(T,null,{default:t(()=>[m("div",{class:"group flex flex-col space-y-2 cursor-pointer",onClick:W(h,["stop"]),onDblclick:i},[m("div",{class:Pe(["w-full aspect-video rounded-xl overflow-hidden transition-all",[b.selected&&"border-2 border-primary-500"]])},[o(s)?(a(),v("img",{key:0,src:o(s),class:"w-full h-full object-cover group-hover:scale-105 transition-all"},null,8,dt)):ce("",!0),m("div",pt,[e(o(Je),{size:24,class:"opacity-30 -rotate-45 group-hover:scale-110 transition-all"})])],2),m("div",mt,[m("div",ft,q(b.flow.name),1),m("div",ht,q(b.flow.description),1)])],32)]),_:1}),e(R,{class:"w-44"},{default:t(()=>[e(k,{onClick:i},{default:t(()=>[e(o(Fe),{size:15,class:"mr-1.5 opacity-60"}),x(" 打开工作流 ")]),_:1}),e(F),e(k,{onClick:g[0]||(g[0]=u=>r.value=!0)},{default:t(()=>[e(o(Te),{size:15,class:"mr-1.5 opacity-60"}),x(" 重命名 ")]),_:1}),e(k,null,{default:t(()=>[e(o(Ce),{size:15,class:"mr-1.5 opacity-60"}),x(" 设置封面 ")]),_:1}),e(F),e(k,{onClick:g[1]||(g[1]=u=>d.value=!0)},{default:t(()=>[e(o(Y),{size:15,class:"mr-1.5 opacity-60"}),x(" 删除 ")]),_:1})]),_:1})]),_:1}),e(O,{"dialog-open":o(r),"onUpdate:dialogOpen":g[3]||(g[3]=u=>V(r)?r.value=u:null),flow:b.flow,onOnUpdate:w},null,8,["dialog-open","flow"]),e(B,{open:o(d),"onUpdate:open":g[4]||(g[4]=u=>V(d)?d.value=u:null),flows:[b.flow],onOnDeleted:C},null,8,["open","flows"])],64)}}}),gt={class:"w-full"},vt={key:0,class:"flows-grid"},yt={key:1,class:"flex items-center justify-center h-[calc(100vh-300px)] text-center text-zinc-600"},xt=$({__name:"FlowsContainer",props:{currentFolder:{}},setup(_){const n=_,c=D([]),l=D([]),s=P(()=>l.value.map(r=>r.id));async function f(){var r;return await _e.query({folderId:(r=n.currentFolder)==null?void 0:r.id})}async function i(){c.value=await f()}function p(r){const w=l.value.findIndex(d=>d.id===r.id);w===-1?l.value.push(r):l.value.splice(w,1)}function h(r){r.stopPropagation(),l.value=[]}return re(async()=>{await i(),document.addEventListener("click",h)}),Re(()=>{document.removeEventListener("click",h)}),Ae(()=>n.currentFolder,async()=>{await i()}),M("Flows::Refresh").on(async()=>{await i()}),(r,w)=>{const d=wt;return a(),v("div",gt,[o(c).length?(a(),v("div",vt,[(a(!0),v(I,null,ie(o(c),C=>(a(),y(d,{key:C.id,flow:C,selected:o(s).includes(C.id),onOnSelect:b=>p(C)},null,8,["flow","selected","onOnSelect"]))),128))])):(a(),v("div",yt," 还没有工作流~ "))])}}}),he=$({__name:"DialogTrigger",props:{asChild:{type:Boolean},as:{}},setup(_){const n=_;return(c,l)=>(a(),y(o(Le),Oe(je(n)),{default:t(()=>[X(c.$slots,"default")]),_:3},16))}}),Ft=$({__name:"NewFolder",setup(_){const n=D(!1),c=ee(te({name:H().min(2).max(50),desc:H().optional()})),s=oe({validationSchema:c}).handleSubmit(async f=>{const i=f.name,p=f.desc??"";await Q.create({name:i,description:p})?(E.success("文件夹创建成功"),n.value=!1,M("Folders::Refresh").emit()):E.error("文件夹创建失败, 请重试")},()=>{E.error("文件夹名称必须在 2 到 50 个字符之间")});return(f,i)=>{const p=K,h=he,r=ne,w=se,d=de,C=pe,b=ae,g=me,T=fe,k=ue("auto-animate");return a(),y(T,{open:o(n),"onUpdate:open":i[1]||(i[1]=F=>V(n)?n.value=F:null)},{default:t(()=>[e(h,{"as-child":""},{default:t(()=>[e(p,{class:"w-full rounded-[3px]"},{default:t(()=>[e(o(rt),{size:16,class:"mr-1.5"}),x(" 新建文件夹 ")]),_:1})]),_:1}),e(g,{class:"w-[480px]"},{default:t(()=>[e(w,null,{default:t(()=>[e(r,null,{default:t(()=>[x("新建文件夹")]),_:1})]),_:1}),m("form",{class:"space-y-4",onSubmit:i[0]||(i[0]=(...F)=>o(s)&&o(s)(...F))},[e(o(j),{name:"name"},{default:t(({componentField:F})=>[N((a(),y(o(L),null,{default:t(()=>[e(o(U),null,{default:t(()=>[e(d,z({autofocus:"",placeholder:"文件夹名称",class:"col-span-3"},F),null,16)]),_:2},1024)]),_:2},1024)),[[k]])]),_:1}),e(o(j),{name:"desc"},{default:t(({componentField:F})=>[N((a(),y(o(L),null,{default:t(()=>[e(o(U),null,{default:t(()=>[e(C,z({placeholder:"文件夹描述 [可选]",class:"col-span-3"},F),null,16)]),_:2},1024)]),_:2},1024)),[[k]])]),_:1}),e(b,null,{default:t(()=>[e(p,{type:"submit",onClick:o(s)},{default:t(()=>[x("确定")]),_:1},8,["onClick"])]),_:1})],32)]),_:1})]),_:1},8,["open"])}}}),Ct=$({__name:"Separator",props:{orientation:{},decorative:{type:Boolean},asChild:{type:Boolean},as:{},class:{}},setup(_){const n=_,c=P(()=>{const{class:l,...s}=n;return s});return(l,s)=>(a(),y(o(Ue),z(c.value,{class:o(G)("shrink-0 bg-border",n.orientation==="vertical"?"w-px h-full":"h-px w-full",n.class)}),null,16,["class"]))}}),$t=$({__name:"CommandEmpty",props:{asChild:{type:Boolean},as:{},class:{}},setup(_){const n=_,c=P(()=>{const{class:l,...s}=n;return s});return(l,s)=>(a(),y(o(qe),z(c.value,{class:o(G)("py-6 text-center text-sm",n.class)}),{default:t(()=>[X(l.$slots,"default")]),_:3},16,["class"]))}}),bt={class:"flex items-center border-b px-3","cmdk-input-wrapper":""},kt=$({inheritAttrs:!1,__name:"CommandInput",props:{type:{},disabled:{type:Boolean},autoFocus:{type:Boolean},asChild:{type:Boolean},as:{},class:{}},setup(_){const n=_,c=P(()=>{const{class:s,...f}=n;return f}),l=Ee(c);return(s,f)=>(a(),v("div",bt,[e(o(ut),{class:"mr-2 h-4 w-4 shrink-0 opacity-50"}),e(o(Ne),z({...o(l),...s.$attrs},{"auto-focus":"",class:o(G)("flex h-10 w-full rounded-md bg-transparent py-3 text-sm outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50",n.class)}),null,16,["class"])]))}}),Dt={class:"flex items-center justify-between w-full"},St={class:"flex items-center gap-2 opacity-0 group-hover:opacity-100"},zt={key:1,class:"p-2"},Tt=m("span",{class:"flex items-center justify-center w-full h-20 text-sm text-muted-foreground select-none"}," 没有文件夹 ",-1),we=$({__name:"FoldersCombobox",emits:["onFolderChange"],setup(_,{emit:n}){const c=n,l=D(!1),s=D([]),f=D();async function i(){return await Q.queryAll()}async function p(){s.value=await i()}async function h(w){await Q.delete(w),await p()}function r(w){f.value=w,c("onFolderChange",w)}return re(async()=>{await p()}),M("Folders::Refresh").on(async()=>{await p()}),(w,d)=>{const C=K,b=We,g=kt,T=$t,k=Qe,F=Ve,R=He,A=Ge,O=Ze,B=Ct,u=Ft,J=Xe,ge=Ye,ve=et,ye=tt,xe=ot;return a(),y(xe,{open:o(l),"onUpdate:open":d[1]||(d[1]=S=>V(l)?l.value=S:null)},{default:t(()=>[e(b,{"as-child":""},{default:t(()=>[e(C,{variant:"outline",size:"sm",class:"w-[180px] justify-between"},{default:t(()=>[o(f)?(a(),v(I,{key:0},[x(q(o(f).name),1)],64)):(a(),v(I,{key:1},[x("全部")],64)),e(o(lt),{class:"opacity-50",size:15})]),_:1})]),_:1}),e(ye,{class:"p-0 w-60",side:"right",align:"start"},{default:t(()=>[e(ve,null,{default:t(()=>[o(s).length>0?(a(),v(I,{key:0},[e(g,{placeholder:"搜索文件夹.."}),e(ge,null,{default:t(()=>[e(T,null,{default:t(()=>[x("没有找到文件夹")]),_:1}),e(J,null,{default:t(()=>[e(k,{class:"cursor-pointer hover:bg-primary-foreground hover:text-primary-background",value:"all",onSelect:d[0]||(d[0]=()=>{r(void 0),l.value=!1})},{default:t(()=>[x(" 全部 ")]),_:1}),e(O,null,{default:t(()=>[(a(!0),v(I,null,ie(o(s),S=>(a(),y(A,{"delay-duration":0},{default:t(()=>[e(F,{as:"div"},{default:t(()=>[(a(),y(k,{key:S.id,value:S.name,onSelect:()=>{r(S),l.value=!1},class:"group cursor-pointer hover:bg-primary-foreground hover:text-primary-background"},{default:t(()=>[m("span",Dt,[m("span",null,q(S.name),1),m("span",St,[e(C,{size:"icon",class:"w-6 h-6",variant:"destructive",onClick:W(Et=>h(S.id),["stop"])},{default:t(()=>[e(o(Y),{size:14})]),_:2},1032,["onClick"])])])]),_:2},1032,["value","onSelect"]))]),_:2},1024),S.description?(a(),y(R,{key:0,side:"right"},{default:t(()=>[m("span",null,q(S.description),1)]),_:2},1024)):ce("",!0)]),_:2},1024))),256))]),_:1}),e(B,{class:"my-1"}),e(u)]),_:1})]),_:1})],64)):(a(),v("div",zt,[Tt,e(u)]))]),_:1})]),_:1})]),_:1},8,["open"])}}}),Bt={class:"flex justify-between w-full"},Mt=$({__name:"FlowsFilter",setup(_){function n(c){M("Flows::Filter::Folder").emit(c)}return(c,l)=>{const s=we;return a(),v("div",Bt,[e(s,{onOnFolderChange:n})])}}}),It={class:"flex items-center space-x-2"},Pt={class:"flex items-center justify-between w-full"},Rt={class:"flex items-center gap-2"},At=m("span",{class:"text-xs text-muted-foreground"},"选择文件夹",-1),Ot=$({__name:"NewFlow",setup(_){const n=D(!1),c=ee(te({name:H().min(2).max(50),desc:H().optional(),useDefault:Me().optional()})),l=oe({validationSchema:c}),s=D(),f=le(),i=l.handleSubmit(async p=>{const h=p.name,r=p.desc??"",w=p.useDefault,d=await _e.create({name:h,description:r,folder:s.value,data:w?nt:st});d?(n.value=!1,f.push({name:"Flow",params:{id:String(d.id)}})):E.error("工作流创建失败, 请重试")},p=>{console.log(p),E.error("工作流标题必须在 2 到 50 个字符之间")});return(p,h)=>{const r=K,w=he,d=ne,C=se,b=de,g=pe,T=at,k=_t,F=we,R=ae,A=me,O=fe,B=ue("auto-animate");return a(),y(O,{open:o(n),"onUpdate:open":h[2]||(h[2]=u=>V(n)?n.value=u:null)},{default:t(()=>[e(w,{"as-child":""},{default:t(()=>[e(r,{class:"w-44 gap-1",variant:"outline",size:"hg"},{default:t(()=>[e(o(it),{size:16}),x(" 新建工作流 ")]),_:1})]),_:1}),e(A,{class:"w-[480px]"},{default:t(()=>[e(C,null,{default:t(()=>[e(d,null,{default:t(()=>[x("新建工作流")]),_:1})]),_:1}),m("form",{class:"space-y-4",onSubmit:h[1]||(h[1]=(...u)=>o(i)&&o(i)(...u))},[e(o(j),{name:"name"},{default:t(({componentField:u})=>[N((a(),y(o(L),null,{default:t(()=>[e(o(U),null,{default:t(()=>[e(b,z({autofocus:"",placeholder:"工作流标题",class:"col-span-3"},u),null,16)]),_:2},1024)]),_:2},1024)),[[B]])]),_:1}),e(o(j),{name:"desc"},{default:t(({componentField:u})=>[N((a(),y(o(L),null,{default:t(()=>[e(o(U),null,{default:t(()=>[e(g,z({placeholder:"工作流描述 [可选]",class:"col-span-3"},u),null,16)]),_:2},1024)]),_:2},1024)),[[B]])]),_:1}),e(o(j),{name:"useDefault"},{default:t(({value:u,handleChange:J})=>[N((a(),y(o(L),null,{default:t(()=>[e(o(U),null,{default:t(()=>[m("div",It,[e(T,{id:"use-default",checked:u,"onUpdate:checked":J},null,8,["checked","onUpdate:checked"]),e(k,{for:"use-default"},{default:t(()=>[x("使用默认工作流")]),_:1})])]),_:2},1024)]),_:2},1024)),[[B]])]),_:1}),e(R,null,{default:t(()=>[m("div",Pt,[m("span",Rt,[At,e(F,{onOnFolderChange:h[0]||(h[0]=u=>s.value=u==null?void 0:u.id)})]),e(r,{type:"submit",onClick:o(i)},{default:t(()=>[x("确定")]),_:1},8,["onClick"])])]),_:1})],32)]),_:1})]),_:1},8,["open"])}}}),jt={class:"flex justify-between w-full"},Lt={class:"flex gap-5"},Ut=$({__name:"FlowsActions",setup(_){return(n,c)=>{const l=Ot,s=K;return a(),v("div",jt,[m("div",Lt,[e(l),e(s,{class:"w-44 gap-1",variant:"outline",size:"hg"},{default:t(()=>[e(o(ct),{size:16}),x(" 导入工作流 ")]),_:1})])])}}}),qt={class:"gap-5"},Qt=$({__name:"Flows",setup(_){const n=D();return M("Flows::Filter::Folder").on(c=>{n.value=c}),(c,l)=>{const s=Ut,f=Mt,i=xt;return a(),v("div",qt,[e(s),e(f),e(i,{"current-folder":o(n)},null,8,["current-folder"])])}}});export{Qt as default};