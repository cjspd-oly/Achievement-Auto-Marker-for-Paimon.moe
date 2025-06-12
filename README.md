# Genshin Achievement Auto-Marker

🎮 **Mark your Genshin Impact achievements automatically using just a video** — no login, no password, no API keys.

> 🏆 Built for "Wonders of the World" (800+ achievements), but works for all 1500+. Just process each section separately.

---

## 🚀 Quick Start

1. 📸 Record a **60s video** of your achievement list — cropped to show only the right side.
2. 💾 Save the video as `sample.mp4` in the root folder.
3. 🐍 Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```
4. ▶️ Run the program:

   ```bash
   python main.py
   ```

> 💡 You can also convert a folder of screenshots into a **1 FPS video** and process that.

---

## 🧠 How It Works

1. Converts video into image frames.
2. Filters out duplicate frames.
3. Extracts text using OCR.
4. Matches achievements using a local Paimon.moe database.
5. Generates an importable file for [paimon.moe](https://paimon.moe).

✅ **Tested** on 700+ achievements → 600+ matched correctly, **0 incorrect**.

⚠️ *It never falsely marks uncompleted achievements.*

---

## 📂 Folder Structure (After First Run)

* `data/frames/` → Extracted frames
* `data/ocr/` → OCR text (do not edit)
* `data/error/` → Mismatches & logs
* `uploads/` → Final file for paimon.moe
* `logs/` → Debug info

---

## ⚙️ Configuration

Two config files control the program:

### `frame_extraction.toml`

```toml
diff_threshold = 1000000
```

* Filters similar frames to reduce processing.
* 🔼 Higher = stricter, fewer frames kept.
* 🔽 Lower = more frames, better accuracy, slower.
* 📌 Suggested range: 500000–2000000

### `import_generator.toml`

```toml
threshold = 90
```

* Fuzzy match accuracy between OCR and database.
* 🔼 Higher = stricter (fewer false positives).
* 🔽 Lower = more lenient (may increase errors).
* 📌 Suggested range: 85–92

🎞️ Default video: `sample.mp4` — can be changed post-init.

---

## 📽️ Recording Tips

* 📍 Crop to only the right achievement panel
* ✅ Start from first **completed** achievement
* 📺 Use **1080p** or better quality
* 🖱️ Scroll slowly with scrollbar
* 🎞️ Use 60–120 FPS for best OCR clarity

---

## 🧪 System Performance

⏱️ On RTX 3060, Ryzen 5 5600g, 16GB RAM:

* \~15 minutes per 1-minute video
* OCR is the bottleneck
* GPU highly recommended

---

## 🖼️ Screenshot Mode (Not Recommended)

* Take \~100 screenshots (\~8 achievements per screen) (manually)
* Filenames don’t matter
* 🌀 Convert to **1 FPS video** and process normally
* ✅ Usually achieves **95-100% accuracy**

---

## 🔒 Safe & Private

✅ **100% offline and secure**:

* ❌ No login / UID / account access
* ❌ No online API calls or uploads
* ✅ Works only on local pre-recorded video/screenshots
* ✅ Output file is manually uploaded by you

---

## 📌 Do Not Edit

* `data/ocr/` → OCR raw data. Leave untouched.
* `paimon_data/` → Stores the achievement DB. Only update with new Genshin versions (or ping me).

📦 If you're uploading using multiple videos:

* Download your current file from paimon.moe and replace the content with `raw.json` in `paimon_data/` folder.
* This allows the tool to only mark **new achievements**.
* You can also reuse and merge output from `uploads/` with existing raw\.json manually.
* ⚠️ Future versions will support **auto-merging** to make this seamless.

---

## ⚠️ Limitations

* 🔁 **Checklist Achievements:**

  * Paimon.moe splits some achievements into checklists (e.g., 3 parts).
  * This tool **only marks the first item** in such checklists **if** the main achievement is matched.
  * ⚠️ You’ll need to manually mark the remaining checklist parts (usually <50).

* ❗ **Not 100% accurate:**

  * A few achievements might remain unmarked — review and mark them manually.
  * ✅ Still a huge time-saver: instead of manually marking 800, you'll likely only need to verify \~100–200 depending on what you’ve already done.

---

## 📸 Screenshots & Demo

* 🖼️ Video/screenshot input: Only the right achievement list panel.
* 🎞️ Demo: Scroll from first completed, 1080p, readable text.

🎬 Submit your scroll video in issues if you’d like it featured!

---

## 📝 To-Do (Planned Features)

* [ ] GUI / No-code mode
* [ ] Auto-update DB from paimon.moe.
* [ ] Smart merging of older uploads files
* [ ] Error/fuzzy matching insights

---

## 🙌 Contribute or Suggest

Got ideas? PRs and issues welcome! Even just suggestions or video tests are appreciated 💡

---

> 😅 I made this after manually marking 700+ achievements. A friend didn’t want to share her account, so I finally built this tool.

---

### Coming Soon
📄 See [`ADVANCED.md`](ADVANCED.md) for config tweaks
📄 See [`FAQ.md`](FAQ.md) for answers
📄 See [`CHANGELOG.md`](CHANGELOG.md) for version history

---

⭐ Star this repo if it helped you!
