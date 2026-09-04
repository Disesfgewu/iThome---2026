import asyncio
import os
import cv2
import numpy as np
from PIL import Image
from playwright.async_api import async_playwright

async def record_actual_demo():
    base_dir = r"c:\Users\marti\Desktop\iThome---2026"
    output_dir = os.path.join(base_dir, "days", "images", "day29")
    os.makedirs(output_dir, exist_ok=True)
    
    temp_rec_dir = os.path.join(base_dir, "temp_playwright_rec")
    # Clean previous temp recordings if any
    if os.path.exists(temp_rec_dir):
        for f in os.listdir(temp_rec_dir):
            try:
                os.remove(os.path.join(temp_rec_dir, f))
            except Exception:
                pass
    os.makedirs(temp_rec_dir, exist_ok=True)

    print("Starting Playwright to record live browser interaction...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            record_video_dir=temp_rec_dir,
            record_video_size={"width": 1280, "height": 720},
            viewport={"width": 1280, "height": 720}
        )
        page = await context.new_page()

        # ==========================================
        # Stage 1: Setup Page (國立高雄師範大學 軟體工程與管理學系)
        # ==========================================
        print("1. Navigating to http://localhost:5173...")
        await page.goto("http://localhost:5173")
        await page.wait_for_timeout(2000)

        print("2. Filling Target School and Major...")
        school_input = page.locator("input[placeholder*='目標學校']")
        major_input = page.locator("input[placeholder*='目標系所']")
        
        await school_input.click()
        await school_input.fill("")
        await school_input.type("國立高雄師範大學", delay=70)
        await page.wait_for_timeout(500)

        await major_input.click()
        await major_input.fill("")
        await major_input.type("軟體工程與管理學系", delay=70)
        await page.wait_for_timeout(800)

        # Scroll down to reveal persona mode and profile details
        await page.mouse.wheel(0, 380)
        await page.wait_for_timeout(1500)

        # Click Launch Button
        print("3. Launching interview chamber...")
        launch_btn = page.locator("button:has-text('啟動模擬面試艙')")
        await launch_btn.click()

        # ==========================================
        # Stage 2: Mock Interview Chamber (Turns 1-3)
        # ==========================================
        print("4. Waiting for Question 1 in cabin...")
        await page.wait_for_selector("textarea", state="visible", timeout=35000)
        await page.wait_for_timeout(2500)

        stop_tts = page.locator("button:has-text('停止語音朗讀')")
        if await stop_tts.count() > 0:
            try:
                await stop_tts.first.click()
            except Exception:
                pass

        print("5. Typing Answer 1...")
        textarea = page.locator("textarea")
        ans1 = "教授您好，我是報考高師大軟體工程與管理學系的林同學。高中期間我通過 APCS 觀念5級/實作4級，並主導開發了服務全校1200人的自習室預約系統。我期許能在貴系兼具軟體架構設計與敏捷專案管理的環境中深造。"
        await textarea.click()
        await textarea.type(ans1, delay=15)
        await page.wait_for_timeout(1000)

        send_btn = page.locator("button:has-text('確認送出回答')")
        await send_btn.click()

        # Turn 2
        print("6. Waiting for Question 2 stream to finish...")
        await page.wait_for_selector("button:has-text('確認送出回答'):not([disabled])", timeout=40000)
        await page.wait_for_timeout(1500)
        if await stop_tts.count() > 0:
            try:
                await stop_tts.first.click()
            except Exception:
                pass

        print("7. Typing Answer 2...")
        ans2 = "在開發預約系統時，我遇到高並發 Concurrent Booking 導致的資料庫鎖定問題。我引入 Redis 記憶體快取佇列鎖與樂觀鎖機制，成功解決衝突並降低延遲 65%，維持 100% 資料一致性。"
        await textarea.click()
        await textarea.type(ans2, delay=15)
        await page.wait_for_timeout(1000)
        await send_btn.click()

        # Turn 3
        print("8. Waiting for Question 3 stream to finish...")
        await page.wait_for_selector("button:has-text('確認送出回答'):not([disabled])", timeout=40000)
        await page.wait_for_timeout(1500)
        if await stop_tts.count() > 0:
            try:
                await stop_tts.first.click()
            except Exception:
                pass

        print("9. Typing Answer 3...")
        ans3 = "進入高師大軟管系後，我計畫深化 DevOps CI/CD 自動化與雲端微服務架構，結合敏捷專案管理決策課程，期許未來擔任大型軟體工程團隊的 Tech Lead 與系統架構師。"
        await textarea.click()
        await textarea.type(ans3, delay=15)
        await page.wait_for_timeout(1000)

        print("10. Submitting Answer 3 (Auto-transition to Strategic Evaluation Report)...")
        await send_btn.click()

        # ==========================================
        # Stage 3: Full Evaluation Report Page
        # ==========================================
        print("11. Waiting for Report Page radar canvas to render (Gemma LLM STAR analysis)...")
        # Give generous 180s timeout so Gemma LLM generation completes smoothly
        await page.wait_for_selector("canvas", state="visible", timeout=180000)
        print("Report page loaded successfully with Radar Canvas!")
        await page.wait_for_timeout(4000)

        # Smooth scroll to view overall score and radar chart
        print("12. Exploring Report Page radar chart and strategic insights...")
        for _ in range(6):
            await page.mouse.wheel(0, 160)
            await page.wait_for_timeout(400)
        await page.wait_for_timeout(2000)

        # Expand STAR question diagnosis accordions
        print("13. Expanding STAR accordions Q1, Q2, Q3...")
        acc_btns = page.locator("button:has(span:has-text('expand_more'))")
        acc_count = await acc_btns.count()
        print(f"Found {acc_count} accordion buttons")
        
        # Sequentially expand Turn 1, Turn 2, Turn 3 to display STAR analysis
        for idx in range(min(acc_count, 3)):
            try:
                print(f"Clicking accordion Turn {idx + 1}...")
                await acc_btns.nth(idx).click()
                await page.wait_for_timeout(2500)
                await page.mouse.wheel(0, 120)
                await page.wait_for_timeout(1000)
            except Exception as e:
                print(f"Click accordion {idx} error: {e}")

        # Scroll down through the opened STAR diagnosis
        for _ in range(6):
            await page.mouse.wheel(0, 150)
            await page.wait_for_timeout(400)
        await page.wait_for_timeout(3000)

        # Scroll back up to export button
        for _ in range(12):
            await page.mouse.wheel(0, -180)
            await page.wait_for_timeout(150)
        await page.wait_for_timeout(1500)

        # Click Export Modal button
        print("14. Opening Export Diagnosis Modal...")
        export_btn = page.locator("button:has-text('匯出 / 下載診斷書')")
        if await export_btn.count() > 0:
            await export_btn.first.click()
            await page.wait_for_timeout(4500)

        print("15. Finalizing recording...")
        await context.close()
        await browser.close()

    # Find the recorded webm file
    webm_files = [f for f in os.listdir(temp_rec_dir) if f.endswith(".webm")]
    if not webm_files:
        print("Error: No webm file was recorded!")
        return

    webm_path = os.path.join(temp_rec_dir, webm_files[0])
    print(f"Recorded webm path: {webm_path} (Size: {os.path.getsize(webm_path)} bytes)")

    # Convert to MP4 and accelerated GIF
    mp4_target = os.path.join(output_dir, "day29_nknu_se_demo.mp4")
    gif_target = os.path.join(output_dir, "day29_nknu_se_demo.gif")

    print(f"Converting {webm_path} to MP4 and accelerated GIF...")
    
    cap = cv2.VideoCapture(webm_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Source video: {width}x{height}, FPS: {fps}, Total frames: {total_frames}")

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out_mp4 = cv2.VideoWriter(mp4_target, fourcc, fps, (width, height))

    gif_frames = []
    frame_idx = 0
    # Sample rate for accelerated GIF (e.g., sample every 8th frame to create a smooth ~4x timelapse)
    sample_rate_gif = 8

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        out_mp4.write(frame)

        if frame_idx % sample_rate_gif == 0:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_frame = Image.fromarray(rgb_frame)
            pil_small = pil_frame.resize((854, 480), Image.Resampling.BILINEAR)
            pil_palette = pil_small.convert("P", palette=Image.Palette.ADAPTIVE, colors=128)
            gif_frames.append(pil_palette)

        frame_idx += 1

    cap.release()
    out_mp4.release()
    print(f"MP4 saved at: {mp4_target} (Size: {os.path.getsize(mp4_target)} bytes)")

    if gif_frames:
        print(f"Saving accelerated GIF with {len(gif_frames)} frames...")
        gif_frames[0].save(
            gif_target,
            save_all=True,
            append_images=gif_frames[1:],
            duration=120,
            loop=0,
            optimize=True
        )
        print(f"Accelerated GIF saved at: {gif_target} (Size: {os.path.getsize(gif_target)} bytes)")

    # Clean up temp webm
    for f in os.listdir(temp_rec_dir):
        try:
            os.remove(os.path.join(temp_rec_dir, f))
        except Exception:
            pass
    try:
        os.rmdir(temp_rec_dir)
    except Exception:
        pass

    print("Completed full demo video and GIF recording!")

if __name__ == "__main__":
    asyncio.run(record_actual_demo())
