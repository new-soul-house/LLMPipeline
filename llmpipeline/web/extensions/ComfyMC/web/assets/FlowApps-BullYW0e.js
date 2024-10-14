import{A as N,F as U,_ as V,a as j,b as L,c as q,d as K,e as P}from"./ContextMenuTrigger.vue_vue_type_script_setup_true_lang-BRUDrEm3.js";import{T as G,a as H,_ as J}from"./RenameDialog.vue_vue_type_script_setup_true_lang-BqU9D-5A.js";import{d as M,h as I,l as Q,p as h,o as a,a as p,c as e,w as r,g as f,q as R,n as W,u as t,s as X,t as b,b as F,v as z,F as O,x as Y,y as Z,z as ee,r as oe,i as te}from"./index-Duqd1f_9.js";import{u as ne,a as k,f as se}from"./Input.vue_vue_type_script_setup_true_lang-BI8tpA8x.js";import{R as le}from"./route-B9Whvd7H.js";import{_ as ae}from"./_plugin-vue_export-helper-DlAUqK2U.js";import"./createLucideIcon-dytpvnWD.js";const ce=["src"],ie={class:"w-full h-full bg-zinc-900 flex items-center justify-center"},re={class:"flex flex-col gap-1"},pe={class:"flex font-medium text-sm opacity-80 select-none"},ue={class:"flex text-xs opacity-30 select-none"},de=M({__name:"FlowAppsItem",props:{flowApp:{},selected:{type:Boolean}},emits:["onSelect"],setup(v,{emit:m}){const s=v,c=m,x=I(()=>s.flowApp.thumbnail),g=Q();function i(){g.push({name:"FlowApp",params:{id:s.flowApp.id}})}const{shift:C}=ne();function A(){C.value?c("onSelect"):i()}const o=h(!1);function _(){k("FlowApps::Refresh").emit()}const l=h(!1);function u(){k("FlowApps::Refresh").emit()}return(d,n)=>{const S=V,y=j,$=L,B=q,D=K,T=J,E=P;return a(),p(O,null,[e(D,{onContextmenu:n[2]||(n[2]=R(()=>{},["prevent"]))},{default:r(()=>[e(S,null,{default:r(()=>[f("div",{class:"group flex flex-col space-y-2 cursor-pointer",onClick:R(A,["stop"]),onDblclick:i},[f("div",{class:W(["w-full aspect-video rounded-xl overflow-hidden transition-all",[d.selected&&"border-2 border-primary-500"]])},[t(x)?(a(),p("img",{key:0,src:t(x),class:"w-full h-full object-cover group-hover:scale-105 transition-all"},null,8,ce)):X("",!0),f("div",ie,[e(t(le),{size:24,class:"opacity-30 -rotate-45 group-hover:scale-110 transition-all"})])],2),f("div",re,[f("div",pe,b(d.flowApp.name),1),f("div",ue,b(d.flowApp.description),1)])],32)]),_:1}),e(B,{class:"w-44"},{default:r(()=>[e(y,{onClick:i},{default:r(()=>[e(t(N),{size:15,class:"mr-1.5 opacity-60"}),F(" 打开 App ")]),_:1}),e($),e(y,{onClick:n[0]||(n[0]=w=>o.value=!0)},{default:r(()=>[e(t(G),{size:15,class:"mr-1.5 opacity-60"}),F(" 重命名 ")]),_:1}),e(y,null,{default:r(()=>[e(t(U),{size:15,class:"mr-1.5 opacity-60"}),F(" 设置封面 ")]),_:1}),e($),e(y,{onClick:n[1]||(n[1]=w=>l.value=!0)},{default:r(()=>[e(t(H),{size:15,class:"mr-1.5 opacity-60"}),F(" 删除 ")]),_:1})]),_:1})]),_:1}),e(T,{"dialog-open":t(o),"onUpdate:dialogOpen":n[3]||(n[3]=w=>z(o)?o.value=w:null),flow:d.flowApp,onOnUpdate:_},null,8,["dialog-open","flow"]),e(E,{open:t(l),"onUpdate:open":n[4]||(n[4]=w=>z(l)?l.value=w:null),flows:[d.flowApp],onOnDeleted:u},null,8,["open","flows"])],64)}}}),fe={class:"w-full"},me={key:0,class:"flows-grid"},_e={key:1,class:"flex items-center justify-center h-[calc(100vh-200px)] text-center text-zinc-600"},we=M({__name:"FlowAppsContainer",props:{currentFolder:{}},setup(v){const m=v,s=h([]),c=h([]),x=I(()=>c.value.map(o=>o.id));async function g(){var o;return await se.query({folderId:(o=m.currentFolder)==null?void 0:o.id})}async function i(){s.value=await g()}function C(o){const _=c.value.findIndex(l=>l.id===o.id);_===-1?c.value.push(o):c.value.splice(_,1)}function A(o){o.stopPropagation(),c.value=[]}return Y(async()=>{await i(),document.addEventListener("click",A)}),Z(()=>{document.removeEventListener("click",A)}),ee(()=>m.currentFolder,async()=>{await i()}),k("Flows::Refresh").on(async()=>{await i()}),(o,_)=>{const l=de;return a(),p("div",fe,[t(s).length?(a(),p("div",me,[(a(!0),p(O,null,oe(t(s),u=>(a(),te(l,{key:u.id,"flow-app":u,selected:t(x).includes(u.id),onOnSelect:d=>C(u)},null,8,["flow-app","selected","onOnSelect"]))),128))])):(a(),p("div",_e," 还没有生成 App~ "))])}}}),ve={};function xe(v,m){const s=we;return a(),p("div",null,[e(s)])}const $e=ae(ve,[["render",xe]]);export{$e as default};