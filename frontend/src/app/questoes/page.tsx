import type { Metadata } from "next";
import Link from "next/link";
import { Estudo } from "@/components/estudo/Estudo";
import { Logo } from "@/components/Ilustracoes";
import s from "./page.module.css";

export const metadata: Metadata = { title: "Questões" };

export default function PaginaQuestoes() {
  return (
    <div className={`container ${s.pagina}`}>
      <header className={s.topo}>
        <Link className={s.logo} href="/">
          <Logo />
        </Link>
      </header>
      <main>
        <Estudo />
      </main>
    </div>
  );
}
