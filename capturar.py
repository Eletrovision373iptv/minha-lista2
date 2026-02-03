import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        link_m3u8 = None

        def intercept(request):
            nonlocal link_m3u8
            if "playlist-1080p.m3u8" in request.url and "sjwt=" in request.url:
                link_m3u8 = request.url

        page.on("request", intercept)

        try:
            await page.goto("https://www.band.com.br/ao-vivo", wait_until="networkidle", timeout=60000)
            await asyncio.sleep(20)
        except Exception as e:
            print(f"Erro: {e}")

        if link_m3u8:
            # FORMATO ESPECIAL PARA XCIPTV
            with open("band.m3u", "w", encoding="utf-8") as f:
                f.write("#EXTM3U\n")
                f.write('#EXTINF:-1 tvg-logo="https://logodownload.org/wp-content/uploads/2014/07/band-logo-0.png" group-title="Canais Abertos",Band HD\n')
                # O segredo para o XCIPTV está na linha abaixo (|User-Agent...)
                f.write(f'{link_m3u8}|User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36&Referer=https://www.band.com.br/\n')
            print("✅ Arquivo atualizado com sucesso!")
        else:
            print("❌ Link não encontrado.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
