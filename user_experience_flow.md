# Dictionary App User Experience Flow

## 1. First Launch Experience

```
┌─────────────────────────────────────────┐
│      WELCOME TO DICTIONARY APP          │
│                                          │
│         📚 Your Smart Dictionary         │
│                                          │
│  Email:    [________________]           │
│  Password: [________________]           │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │          Sign In                    │ │
│  └────────────────────────────────────┘ │
│                                          │
│  New user? [Create Account]             │
│  Continue as guest                      │
└─────────────────────────────────────────┘
```

## 2. Normal Daily Use

### A. System Tray (Minimized State)
```
Windows Taskbar:
[🔍] <- Dictionary icon in system tray (green = active)
```

### B. User Selects Text and Presses Ctrl+Ctrl
```
Browser/Document showing: "The children went to school"
                           ─────────
User selects "went" and presses Ctrl+Ctrl

                    ↓

┌──────────────────────────────────────┐
│ 🔍 went → go                         │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ [VERB] [NOUN] [ADJ]                  │
│ ────────────────────────────────────  │
│                                       │
│ go /ɡoʊ/ verb                        │
│                                       │
│ 1. Move from one place to another    │
│    "I go to work every day"          │
│    ▼ Show more                       │
│                                       │
│ 2. Leave or depart                   │
│    "It's time to go"                 │
│    ▼ Show more                       │
│                                       │
│ ────────────────────────────────────  │
│ ⭐ Add to favorites                   │
│                                       │
│                                       │
│                                       │
└──────────────────────────────────────┘
```

## 2.5 When Free User Runs Out of Searches

```
User tries to search after 50 searches used up:

┌──────────────────────────────────────┐
│        UPGRADE REQUIRED              │
│                                       │
│   You've used all 50 free searches   │
│                                       │
│   Get unlimited searches forever     │
│         Only $20                     │
│                                       │
│  ┌────────────────────────────────┐  │
│  │     Purchase Now - $20         │  │
│  └────────────────────────────────┘  │
│                                       │
│  ┌────────────────────────────────┐  │
│  │     Sign In                    │  │
│  └────────────────────────────────┘  │
│                                       │
│       [Cancel]                        │
└──────────────────────────────────────┘
```

## 3. Settings Panel (With Extensions)

```
┌──────────────────────────────────────────────────────┐
│ ⚙️ Dictionary Settings                               │
│                                                       │
│ [General][Extensions][Account][Languages][About]     │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                                                       │
│ GENERAL                                               │
│ ┌─────────────────────────────────────────────────┐ │
│ │ Hotkey: [Ctrl] + [Ctrl]  [Change]              │ │
│ │                                                 │ │
│ │ ☑ Start with Windows                           │ │
│ │ ☑ Launch minimized                             │ │
│ │ ☐ Show notification on startup                 │ │
│ │ ☑ Check for updates automatically              │ │
│ └─────────────────────────────────────────────────┘ │
│                                                       │
│ [Apply]  [Cancel]                                     │
└──────────────────────────────────────────────────────┘
```

## 3.1 Extensions Tab (Like Obsidian)

```
┌──────────────────────────────────────────────────────┐
│ ⚙️ Dictionary Settings                               │
│                                                       │
│ [General][Extensions][Account][Languages][About]     │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                    EXTENSIONS                         │
│ ┌─────────────────────────────────────────────────┐ │
│ │ Installed (7)                    [Browse Store] │ │
│ │                                                 │ │
│ │ ☑ Core UI                          v1.0.0 [⚙️] │ │
│ │   Default user interface                       │ │
│ │                                                 │ │
│ │ ☑ Favorites Manager                v1.0.0 [⚙️] │ │
│ │   Save and organize favorite words             │ │
│ │                                                 │ │
│ │ ☑ Search History                   v1.0.0 [⚙️] │ │
│ │   Track your search history                    │ │
│ │                                                 │ │
│ │ ☐ Vim Mode                         v0.5.2 [⚙️] │ │
│ │   Navigate with vim keybindings   [Enable]     │ │
│ │                                                 │ │
│ │ ☑ Dark Theme                       v1.2.1 [⚙️] │ │
│ │   Beautiful dark mode interface                │ │
│ │                                                 │ │
│ │ ☑ Anki Export                      v2.0.0 [⚙️] │ │
│ │   Export definitions to Anki                   │ │
│ │                                                 │ │
│ │ ☐ AI Enhancer (Premium)            v1.0.0 [⚙️] │ │
│ │   AI-powered definition enhancement [$4.99]    │ │
│ │                                                 │ │
│ │ [Safe Mode] [Reload Extensions] [Developer Mode]│ │
│ └─────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
```

## 3.2 Extension Store (Like Obsidian Community Plugins)

```
┌──────────────────────────────────────────────────────┐
│ 🏪 Extension Store                                   │
│                                                       │
│ Search: [________________] [🔍]                      │
│                                                       │
│ Sort by: [Most Popular ▼]  Filter: [All ▼]         │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ ┌─────────────────────────────────────────────────┐ │
│ │ 📦 Vim Mode               ⬇️ 15.2k  ⭐ 4.8     │ │
│ │ by vim-master                                  │ │
│ │ Complete vim keybindings for navigation        │ │
│ │                                   [Install]    │ │
│ │                                                 │ │
│ │ 🎨 Theme Collection        ⬇️ 45.1k  ⭐ 4.9     │ │
│ │ by design-pro                                  │ │
│ │ 20+ beautiful themes for your dictionary       │ │
│ │                                   [Install]    │ │
│ │                                                 │ │
│ │ 📊 Study Analytics         ⬇️ 8.9k   ⭐ 4.6     │ │
│ │ by data-viz                                    │ │
│ │ Track your learning progress with charts       │ │
│ │                                   [Install]    │ │
│ │                                                 │ │
│ │ 🔄 Cloud Sync (Premium)    ⬇️ 12.3k  ⭐ 4.7     │ │
│ │ by sync-master                      [$2.99]    │ │
│ │ Sync across all your devices                   │ │
│ │                                   [Purchase]   │ │
│ │                                                 │ │
│ │ 🤖 AI Translator           ⬇️ 6.5k   ⭐ 4.5     │ │
│ │ by polyglot-ai                      [$4.99]    │ │
│ │ Translate to 100+ languages with AI            │ │
│ │                                   [Purchase]   │ │
│ └─────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
```

## 3.3 Extension Settings (Individual Plugin Config)

```
┌──────────────────────────────────────────────────────┐
│ ⚙️ Anki Export Settings                             │
│                                                       │
│ ┌─────────────────────────────────────────────────┐ │
│ │ Export Format:                                  │ │
│ │ ○ Basic (Front: Word, Back: Definition)        │ │
│ │ ● Advanced (With examples and etymology)       │ │
│ │ ○ Custom template                               │ │
│ │                                                 │ │
│ │ Deck Name: [English Vocabulary    ]            │ │
│ │                                                 │ │
│ │ Tags: [dictionary, english         ]            │ │
│ │                                                 │ │
│ │ ☑ Include pronunciation                        │ │
│ │ ☑ Include example sentences                    │ │
│ │ ☐ Include synonyms                             │ │
│ │ ☑ Auto-export favorites                        │ │
│ │                                                 │ │
│ │ AnkiConnect URL: [http://localhost:8765]       │ │
│ │                                                 │ │
│ │ [Test Connection]  [Export Now]                │ │
│ └─────────────────────────────────────────────────┘ │
│                                                       │
│ [Save]  [Cancel]  [Uninstall Extension]              │
└──────────────────────────────────────────────────────┘
```

## 4. Account Tab (Updated for Extensions)

```
┌──────────────────────────────────────────────────────┐
│ ⚙️ Dictionary Settings                               │
│                                                       │
│ [General][Extensions][Account][Languages][About]     │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                      ACCOUNT                          │
│ ┌─────────────────────────────────────────────────┐ │
│ │ License Status: FREE USER (50 searches used)   │ │
│ │ Email: guest_user_12345                        │ │
│ │                                                 │ │
│ │ ┌─────────────────────────────────────────┐   │ │
│ │ │   🎯 UPGRADE TO PRO - $20               │   │ │
│ │ │                                          │   │ │
│ │ │   ✓ Unlimited searches forever          │   │ │
│ │ │   ✓ Access to Pro extensions            │   │ │
│ │ │   ✓ Priority support                    │   │ │
│ │ │   ✓ Early access to new features        │   │ │
│ │ │                                          │   │ │
│ │ │        [Upgrade Now - $20]              │   │ │
│ │ └─────────────────────────────────────────┘   │ │
│ │                                                 │ │
│ │ Purchased Extensions:                          │ │
│ │ • None yet                                     │ │
│ │                                                 │ │
│ │ [Manage Licenses]  [Restore Purchases]         │ │
│ └─────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
```

## 4.1 Premium User Account Tab

```
┌──────────────────────────────────────────────────────┐
│ ⚙️ Dictionary Settings                               │
│                                                       │
│ [General][Extensions][Account][Languages][About]     │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                      ACCOUNT                          │
│ ┌─────────────────────────────────────────────────┐ │
│ │ License Status: ✅ PRO USER                    │ │
│ │ Email: user@example.com                        │ │
│ │                                                 │ │
│ │                                                 │ │
│ │                                                 │ │
│ │                                                   │ │
│ │                                                 │ │
│ │                                                 │ │
│ │                                                  │ │
│ │                                                 │ │
│ │ Purchased Extensions:                          │ │
│ │ • AI Enhancer ($4.99) - Active                │ │
│ │ • Cloud Sync ($2.99) - Active                 │ │
│ │ • Language Pack: German ($1.99) - Active      │ │
│ │                                                 │ │
│ │                                                  │ │
│ │                                                 │ │
│ │                                                    │ │
│ └─────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
```

## 5. Purchase Flow

```
User clicks "Buy Now - $20"
            ↓
┌──────────────────────────────────────────────────────┐
│          SECURE CHECKOUT - STRIPE                     │
│                                                        │
│  Dictionary App - Lifetime Access                     │
│  $20.00 USD (one-time payment)                       │
│                                                        │
│  Email: [user@example.com          ]                 │
│                                                        │
│  Card: [4242 4242 4242 4242        ]                 │
│  Exp:  [12/25]  CVV: [123]                          │
│                                                        │
│  [Complete Purchase]                                  │
│                                                        │
│  🔒 Secured by Stripe                                 │
└──────────────────────────────────────────────────────┘
            ↓
┌──────────────────────────────────────────────────────┐
│            ✅ PURCHASE SUCCESSFUL!                     │
│                                                        │
│    Thank you for your purchase!                       │
│    You now have unlimited searches forever.           │
│                                                        │
│            [Start Using Dictionary]                   │
└──────────────────────────────────────────────────────┘
```

## 6. Premium User Experience

### Same popup, but no search limit:
```
┌──────────────────────────────────────┐
│ 🔍 children → child                  │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ [NOUN] [VERB]                         │
│ ────────────────────────────────────  │
│                                       │
│ child /tʃaɪld/ noun                  │
│                                       │
│ 1. A young human being                │
│    "The children are playing"        │
│    ▼ Show more examples              │
│                                       │
│ 2. Son or daughter of any age        │
│    "They have three children"        │
│                                       │
│ Synonyms: kid, youngster, minor      │
│                                       │
│ ────────────────────────────────────  │
│ ⭐ Add to favorites                   │
│ 📋 Copy definition                   │
│                                       │
│                                         │
└──────────────────────────────────────────┘
```

## 7. Languages Tab

```
┌──────────────────────────────────────────────────────┐
│ ⚙️ Dictionary Settings                               │
│                                                       │
│ [Hotkeys][POS][Languages][Account][UI]               │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│                    LANGUAGES                          │
│ ┌─────────────────────────────────────────────────┐ │
│ │ Installed Languages:                           │ │
│ │                                                 │ │
│ │ 🇬🇧 English (Default)         [✓ Active]      │ │
│ │ 🇪🇸 Spanish                    [Set Default]   │ │
│ │ 🇫🇷 French                     [Remove]        │ │
│ │                                                 │ │
│ │ ─────────────────────────────────────────────  │ │
│ │ Available for Purchase:                        │ │
│ │                                                 │ │
│ │ 🇩🇪 German        [$1.99] [Buy]               │ │
│ │ 🇮🇹 Italian       [$1.99] [Buy]               │ │
│ │ 🇯🇵 Japanese      [$1.99] [Buy]               │ │
│ │ 🇨🇳 Chinese       [$1.99] [Buy]               │ │
│ └─────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
```

## 8. Search History Dropdown

```
User clicks in search box of popup:
┌──────────────────────────────────────┐
│ 🔍 [________________] 🔽             │
│      │                                │
│      └─ Recent Searches:             │
│         • went (→ go)                │
│         • children (→ child)         │
│         • better (→ good)            │
│         • running (→ run)            │
│                                      │
│                                       │
└──────────────────────────────────────┘
```

## 9. Favorites Panel

```
┌──────────────────────────────────────────────────────┐
│ ⭐ My Favorite Words                                 │
│                                                       │
│ ┌─────────────────────────────────────────────────┐ │
│ │ go (verb) - Added Dec 1                        │ │
│ │   "Move from one place to another"             │ │
│ │                                   [Remove ✕]   │ │
│ │                                                 │ │
│ │ child (noun) - Added Dec 1                     │ │
│ │   "A young human being"                        │ │
│ │                                   [Remove ✕]   │ │
│ │                                                 │ │
│ │ good (adjective) - Added Nov 30                │ │
│ │   "Of high quality or standard"                │ │
│ │                                   [Remove ✕]   │ │
│ └─────────────────────────────────────────────────┘ │
│                                                       │
│ Total favorites: 3                                    │
└──────────────────────────────────────────────────────┘
```

## 10. Developer Mode (Extension Development)

```
┌──────────────────────────────────────────────────────┐
│ 🔧 Developer Mode - Extension Development            │
│                                                       │
│ [Create New][Load Unpacked][Console][API Docs]       │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ │
│ ┌─────────────────────────────────────────────────┐ │
│ │ Development Extensions:                         │ │
│ │                                                 │ │
│ │ 📂 my-custom-theme              [🔄] [📦] [🗑️] │ │
│ │   Path: ~/dev/my-custom-theme                  │ │
│ │   ⚠️ 1 warning, Last reload: 2 mins ago        │ │
│ │                                                 │ │
│ │ 📂 translation-helper           [🔄] [📦] [🗑️] │ │
│ │   Path: ~/dev/translation-helper               │ │
│ │   ✅ No issues, Last reload: 5 mins ago        │ │
│ │                                                 │ │
│ │ Console Output:                                │ │
│ │ ┌─────────────────────────────────────────┐   │ │
│ │ │ [12:34] Plugin loaded: my-custom-theme   │   │ │
│ │ │ [12:34] Registering event listeners...   │   │ │
│ │ │ [12:35] Warning: Deprecated API usage    │   │ │
│ │ │ [12:36] Theme applied successfully       │   │ │
│ │ └─────────────────────────────────────────┘   │ │
│ │                                                 │ │
│ │ [Reload All] [Clear Console] [Export Logs]     │ │
│ └─────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
```

## 10.1 Extension Creation Wizard

```
┌──────────────────────────────────────────────────────┐
│ 🚀 Create New Extension                              │
│                                                       │
│ Extension Name: [My Awesome Plugin      ]            │
│ ID: [my-awesome-plugin                 ]             │
│ Description: [Adds awesome features     ]            │
│ Author: [Your Name                      ]            │
│                                                       │
│ Template:                                             │
│ ○ Blank - Start from scratch                         │
│ ● UI Theme - Customize appearance                    │
│ ○ Language Pack - Add new language                   │
│ ○ Export Plugin - Export to external format          │
│ ○ Search Enhancer - Modify search behavior           │
│                                                       │
│ Features to include:                                 │
│ ☑ Settings page                                      │
│ ☑ Hotkey support                                     │
│ ☐ Database storage                                   │
│ ☐ Network requests                                   │
│                                                       │
│ [Create Extension]  [Cancel]                         │
└──────────────────────────────────────────────────────┘
```

## 11. User Flow Summary

```
START
  │
  ├─→ First Launch
  │     ├─→ Try Free (50 searches)
  │     │     └─→ Use with limits
  │     └─→ Buy ($20)
  │           └─→ Unlimited use
  │
  ├─→ Daily Use
  │     ├─→ Select text
  │     ├─→ Press Ctrl+Ctrl
  │     ├─→ See definition
  │     └─→ Close (ESC)
  │
  └─→ Settings
        ├─→ Change hotkeys
        ├─→ Buy language packs
        ├─→ View favorites
        └─→ Check account status
```

## Key Features Visible to User:

1. **Quick Access**: Lives in system tray, instant popup
2. **Smart Search**: Handles "went"→"go", "children"→"child" 
3. **Extensible**: Full extension marketplace like Obsidian
4. **Clear Monetization**: 
   - Core app: 50 free searches, then $20 forever
5. **Developer Friendly**: 
   - Open API for extension development
   - Hot reload during development
   - Revenue sharing for extension developers
6. **Customizable**: Replace any part via extensions
7. **Simple Core**: Base app just works, extensions add complexity

## Extension Ecosystem Benefits:

### For Users:
- **Choose Your Features**: Only install what you need
- **Community Extensions**: Free extensions from community
- **Premium Options**: Professional extensions for power users
- **Stay Updated**: Extensions update independently
- **Safe Mode**: Disable all extensions if issues arise

### For Developers:
- **Easy Development**: Similar to Obsidian plugin API
- **Monetization**: Sell premium extensions in store
- **Full Control**: Replace even core UI if desired
- **Hot Reload**: Test changes instantly
- **Rich API**: Access to search, UI, storage, events

### For Business:
- **Revenue Streams**:
  - Core app: $20 one-time

- **Ecosystem Growth**: Community builds value
- **Lower Maintenance**: Community maintains extensions