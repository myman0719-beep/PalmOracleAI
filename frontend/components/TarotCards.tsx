"use client";

import {motion} from "framer-motion";

export default function TarotCards(){

return(

<>

<motion.img
src="/tarot1.png"
className="absolute w-24 top-10 left-0"
animate={{
y:[0,-20,0],
rotate:[0,10,0]
}}
transition={{
duration:3,
repeat:Infinity
}}
/>

<motion.img
src="/tarot2.png"
className="absolute w-24 top-20 right-0"
animate={{
y:[0,20,0],
rotate:[0,-10,0]
}}
transition={{
duration:4,
repeat:Infinity
}}
/>

</>

)

}