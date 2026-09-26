"use client";
import type {ReactNode} from "react";
import {motion} from "framer-motion";

type AnimatedCardProps={
  children:ReactNode;
  index:number;
  className?:string;
};

export function AnimatedCard({children,index,className}:AnimatedCardProps){
  return (
    <motion.div
      className={className}
      initial={{opacity:0,x:-20}}
      whileInView={{opacity:1,x:0}}
      viewport={{once:true,margin:"-50px"}}
      transition={{duration:0.3,delay:Math.min(index,8)*0.08,ease:"easeOut"}}
    >
      {children}
    </motion.div>
  );
}