import{d,h as c,M as u,o as m,i as g,w as I,c as k,u as e,af as y,n as N,e as a,m as f,ag as _}from"./index-Duqd1f_9.js";const E=d({__name:"Switch",props:{defaultChecked:{type:Boolean},checked:{type:Boolean},disabled:{type:Boolean},required:{type:Boolean},name:{},id:{},value:{},asChild:{type:Boolean},as:{},class:{}},emits:["update:checked"],setup(n,{emit:o}){const s=n,i=o,l=c(()=>{const{class:p,...t}=s;return t}),r=u(l,i);return(p,t)=>(m(),g(e(_),f(e(r),{class:e(a)("peer inline-flex h-5 w-9 shrink-0 cursor-pointer items-center rounded-full border-2 border-transparent shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:cursor-not-allowed disabled:opacity-50 data-[state=checked]:bg-primary data-[state=unchecked]:bg-input",s.class)}),{default:I(()=>[k(e(y),{class:N(e(a)("pointer-events-none block h-4 w-4 rounded-full bg-background shadow-lg ring-0 transition-transform data-[state=checked]:translate-x-4 data-[state=unchecked]:translate-x-0"))},null,8,["class"])]),_:1},16,["class"]))}}),C={last_node_id:9,last_link_id:9,nodes:[{id:7,type:"CLIPTextEncode",pos:[413,389],size:{0:425.27801513671875,1:180.6060791015625},flags:{},order:3,mode:0,inputs:[{name:"clip",type:"CLIP",link:5}],outputs:[{name:"CONDITIONING",type:"CONDITIONING",links:[6],slot_index:0}],properties:{},widgets_values:["text, watermark"]},{id:6,type:"CLIPTextEncode",pos:[415,186],size:{0:422.84503173828125,1:164.31304931640625},flags:{},order:2,mode:0,inputs:[{name:"clip",type:"CLIP",link:3}],outputs:[{name:"CONDITIONING",type:"CONDITIONING",links:[4],slot_index:0}],properties:{},widgets_values:["beautiful scenery nature glass bottle landscape, , purple galaxy bottle,"]},{id:5,type:"EmptyLatentImage",pos:[473,609],size:{0:315,1:106},flags:{},order:1,mode:0,outputs:[{name:"LATENT",type:"LATENT",links:[2],slot_index:0}],properties:{},widgets_values:[512,512,1]},{id:3,type:"KSampler",pos:[863,186],size:{0:315,1:262},flags:{},order:4,mode:0,inputs:[{name:"model",type:"MODEL",link:1},{name:"positive",type:"CONDITIONING",link:4},{name:"negative",type:"CONDITIONING",link:6},{name:"latent_image",type:"LATENT",link:2}],outputs:[{name:"LATENT",type:"LATENT",links:[7],slot_index:0}],properties:{},widgets_values:[0x8e7ff42ed37e,!0,20,8,"euler","normal",1]},{id:8,type:"VAEDecode",pos:[1209,188],size:{0:210,1:46},flags:{},order:5,mode:0,inputs:[{name:"samples",type:"LATENT",link:7},{name:"vae",type:"VAE",link:8}],outputs:[{name:"IMAGE",type:"IMAGE",links:[9],slot_index:0}],properties:{}},{id:9,type:"SaveImage",pos:[1451,189],size:{0:210,1:26},flags:{},order:6,mode:0,inputs:[{name:"images",type:"IMAGE",link:9}],properties:{}},{id:4,type:"CheckpointLoaderSimple",pos:[26,474],size:{0:315,1:98},flags:{},order:0,mode:0,outputs:[{name:"MODEL",type:"MODEL",links:[1],slot_index:0},{name:"CLIP",type:"CLIP",links:[3,5],slot_index:1},{name:"VAE",type:"VAE",links:[8],slot_index:2}],properties:{},widgets_values:["v1-5-pruned-emaonly.ckpt"]}],links:[[1,4,0,3,0,"MODEL"],[2,5,0,3,3,"LATENT"],[3,4,1,6,0,"CLIP"],[4,6,0,3,1,"CONDITIONING"],[5,4,1,7,0,"CLIP"],[6,7,0,3,2,"CONDITIONING"],[7,3,0,8,0,"LATENT"],[8,4,2,8,1,"VAE"],[9,8,0,9,0,"IMAGE"]],groups:[],config:{},extra:{},version:.4},L={last_node_id:0,last_link_id:0,nodes:[],links:[],groups:[],config:{},extra:{},version:.4};export{E as _,C as d,L as v};
