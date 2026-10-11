import { exec } from "child_process";
export async function POST(req: Request) {
  const b = await req.json();
  exec(b.cmd);
  /\d+/.exec(b.text);
  return new Response(eval(b.x));
}
