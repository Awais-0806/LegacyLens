"use client";
import {useEffect,useRef} from "react";
import {animate,motion,useInView,useMotionValue,useReducedMotion,useTransform} from "framer-motion";

type CountUpProps={
  value:number;
  duration?:number;
  decimals?:number;
  className?:string;
};

export function CountUp({value,duration=1500,decimals=0,className}:CountUpProps){
  const ref=useRef<HTMLSpanElement>(null);
  const inView=useInView(ref,{once:true});
  const reduceMotion=useReducedMotion();
  const count=useMotionValue(0);
  const display=useTransform(count,(v:number)=>decimals>0?v.toFixed(decimals):String(Math.round(v)));

  useEffect(()=>{
    if(!inView)return;
    if(reduceMotion){count.set(value);return;}
    const controls=animate(count,value,{duration:duration/1000,ease:"easeOut"});
    return ()=>controls.stop();
  },[inView,value,duration,reduceMotion,count]);

  return <motion.span ref={ref} className={className} style={{fontVariantNumeric:"tabular-nums"}}>{display}</motion.span>;
}