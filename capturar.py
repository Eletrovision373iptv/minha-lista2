import asyncio
import os
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        # Lançando o navegador
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 720}
        )
        page = await context.new_page()

        link_m3u8 = None

        def intercept(request):
            nonlocal link_m3u8
            # Filtra o arquivo de playlist com o token JWT
            if "playlist-1080p.m3u8" in request.url and "sjwt=" in request.url:
                link_m3u8 = request.url

        page.on("request", intercept)

        print("Acessando o site da Band...")
        try:
            await page.goto("https://www.band.com.br/ao-vivo", wait_until="networkidle", timeout=60000)
            await asyncio.sleep(20) # Tempo para o player carregar
            await page.screenshot(path="debug.png")
        except Exception as e:
            print(f"Erro: {e}")

        # --- AQUI É A PARTE QUE VOCÊ PERGUNTOU ---
        if link_m3u8:
            print(f"✅ Sucesso! Link: {link_m3u8}")
            with open("band.m3u", "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n")
                f.write('#EXTINF:-1 tvg-logo="https://logodownload.org/wp-content/uploads/2014/07/band-logo-0.png" group-title="Canais Abertos",Band HD\n')
                f.write('#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36\n')
                f.write('#EXTVLCOPT:http-referrer=https://www.band.com.br/\n')
                # O "|" ajuda o XCIPTV a entender que o que vem depois são comandos de acesso
                f.write(f'{link_m3u8}|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36&Referer=https://www.band.com.br/\n')
        else:
            print("❌ Falha: Link não encontrado.")
            with open("band.m3u", "w") as f:
                f.write("# Link não capturado nesta rodada")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
