'use client';
import Image from "next/image";
import dynamic from "next/dynamic";
import Navbar from "./components/Navbar"
import Entry from "./components/entry"
export default function Home() {
  return (
    <div>
      <Navbar />
      <Entry/>
    </div>
  );
}
