# EXAM-MASTER

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)
![Python](https://img.shields.io/badge/Python-3.6+-blue.svg)
![Android](https://img.shields.io/badge/Android-v3.0-green.svg)
![Kotlin](https://img.shields.io/badge/Kotlin-1.9.22-purple.svg)
![Platform](https://img.shields.io/badge/Platform-Web%20%7C%20Android-blue.svg)

[English](README.md) | [中文](README_CN.md)

A comprehensive cross-platform exam and quiz management system featuring both **Web** and **Android native** applications. Built with Flask for the web platform and Kotlin/Jetpack Compose for Android, it provides a complete solution for question bank management, multiple practice modes, statistical analysis, and learning progress tracking.

## 🌟 Key Features

### 📱 Multi-Platform Support
- **Web Application**: Modern responsive design supporting desktop and mobile browsers
- **Android App**: Native Android application (v3.0) with smooth mobile experience
- **Offline Capability**: Full offline support with local data storage
- **Data Portability**: Compatible data formats for future cross-platform sync

### 📝 User Management
- **Authentication**: Secure user registration and login system
- **Progress Tracking**: Automatic saving of learning progress and answer history
- **Smart Resume**: System remembers your position and seamlessly continues from where you left off
- **Personalized Dashboard**: Individual statistics and performance metrics

### 📚 Question Bank Management
- **CSV Import**: Bulk import questions from CSV files
- **Multiple Question Types**: Single choice, multiple choice, true/false questions
- **Categorization**: Organize questions by category and difficulty level
- **Question Browser**: Paginated browsing with filtering and quick navigation
- **Flexible Format**: Support for variable number of options (A-E)

### 📋 Practice Modes
- **Random Practice**: Quick practice with randomly selected questions
- **Sequential Practice**: Progress through questions in order with automatic position saving
- **Wrong Questions**: Focus on questions you got wrong for targeted improvement
- **Timed Mode**: Complete questions within set time limits to improve efficiency
- **Exam Simulation**: Full exam environment with batch submission and comprehensive results
- **Browse Mode**: Review all questions with expandable details

### 🔍 Search & Filter
- **Keyword Search**: Find questions by content or ID instantly
- **Smart Filtering**: Filter by question type, category, and difficulty level
- **Global Search**: Search across all pages, not limited to current view
- **Filter Chips**: Mobile-friendly filter interface with one-tap toggles
- **Advanced Queries**: Support for complex search patterns

### 🔖 Personalized Learning
- **Favorites System**: Bookmark important questions with custom tags
- **Answer History**: Complete record of all attempted questions and results
- **Statistical Analysis**: Detailed statistics including accuracy rates, difficulty distribution, and progress
- **Learning Analytics**: Track learning patterns and knowledge mastery
- **Performance Insights**: Identify strengths and areas for improvement

## 💻 Technology Stack

### Web Application
- **Backend**: Python 3.6+ with Flask 2.3.3
- **Database**: SQLite3 with 5 main tables
- **Frontend**: HTML5/CSS3 + JavaScript + Jinja2 templating
- **UI Framework**: Bootstrap utilities + Custom CSS with Material Design inspiration
- **Authentication**: Session-based with secure password hashing
- **Data Format**: CSV import, JSON field storage for flexible options

### Android Application
- **Language**: 100% Kotlin 1.9.22
- **UI Framework**: Jetpack Compose with Material Design 3
- **Architecture**: MVVM + Repository Pattern + Clean Architecture
- **Database**: Room persistence library (SQLite)
- **Dependency Injection**: Hilt
- **Async Processing**: Kotlin Coroutines + Flow
- **Navigation**: Navigation Compose
- **State Management**: StateFlow + Compose State
- **Min SDK**: API 24 (Android 7.0)

## 🚀 Quick Start

### Web Application Deployment

1. **Clone the repository**
   ```bash
   git clone https://github.com/CiE-XinYuChen/EXAM-MASTER.git
   cd EXAM-MASTER
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize database** (automatic on first run)
   The application will automatically:
   - Create SQLite database
   - Initialize tables
   - Import questions from `questions.csv`

4. **Run the application**
   ```bash
   python app.py
   ```
   The application will be available at http://localhost:32220

### Android Application Installation

1. **Download APK directly**
   - Visit the [Releases page](https://github.com/CiE-XinYuChen/EXAM-MASTER/releases)
   - Download the latest `exammaster-v4-debug.apk`
   
2. **Installation steps**
   - Enable "Install from unknown sources" in settings
   - Install the APK
   - The app works completely offline

3. **Build from source** (optional)
   ```bash
   cd ExamMasterAndroid
   ./gradlew assembleDebug
   # APK will be in app/build/outputs/apk/debug/
   ```

4. **Requirements for building**
   - Android Studio Iguana 2023.2.1+
   - Kotlin 1.9.22+
   - Gradle 8.4
   - Android SDK 34

### Question Bank Format

Questions use CSV format with the following fields:

| Field | Description | Example |
|-------|-------------|---------|  
| 题号 (ID) | Unique question identifier | "001" |
| 题干 (Question) | Question content | "What is 2+2?" |
| A, B, C, D, E | Answer options (optional) | "2", "3", "4", "5" |
| 答案 (Answer) | Correct answer(s) | "C" or "ABC" (multiple) |
| 难度 (Difficulty) | Difficulty level | "Easy", "Medium", "Hard" |
| 题型 (Type) | Question type | "单选题", "多选题", "判断题" |
| 类别 (Category) | Question category (optional) | "Math", "Science" |

**Note**: For true/false questions, use "正确" (True) and "错误" (False) as answers.

## 📖 User Guide

### Basic Operations

1. **Registration/Login**: Register on first use, then login with credentials
2. **Navigation**: 
   - **Web**: Top navigation bar with dropdown menus
   - **Android**: Bottom navigation with 5 main sections
3. **Answering Questions**: 
   - Select practice mode (Random/Sequential/Wrong/Timed/Exam)
   - Choose your answer(s)
   - Submit for instant feedback
   - System automatically tracks progress

### Advanced Features

- **Search Questions**: Use the search page to find specific questions by keyword or ID
- **Favorite Questions**: Click the star icon to bookmark, view in "My Favorites"
- **Sequential Practice**: Automatically saves position - resume exactly where you left off
- **Wrong Questions Review**: Automatically collected, practice until mastered
- **Statistics Dashboard**: View comprehensive learning analytics and progress charts
- **Timed Practice**: Set custom time limits for speed training
- **Exam Mode**: Simulate real exam conditions with timed sessions and final scoring

## 🔄 Recent Updates

### v4.0 - Complete Architecture Upgrade (2025-08)
- **🚀 Android App v3.0**: Full native Android app with Jetpack Compose
- **🎨 Material Design 3**: Modern UI with dynamic theming support
- **📊 Enhanced Analytics**: Comprehensive statistics with visual charts
- **🔄 Performance**: Optimized database queries and lazy loading
- **🎯 Smart Features**: Adaptive learning recommendations

### v3.0 - Mobile-First Design (2025-05)
- **📱 Mobile Optimization**: Completely rewritten mobile UI with card-based design
- **🔍 Backend Search**: Server-side search and filtering for better performance
- **🛠 UI Fixes**: Fixed desktop layout issues, improved CSS utilities
- **🎯 Enhanced Filters**: Fixed mobile filter chips, all question types now displayed correctly

### v2.0 - Core Feature Implementation (2025-04)
- **🏗 Architecture**: Refactored core logic for stability
- **💾 Data Persistence**: Optimized storage and query performance
- **🎪 UI Enhancement**: New design system implementation
- **🔧 Sequential Mode**: Smart progress memory system
- **📊 Statistics**: Detailed learning analytics

## 📊 Screenshots
![86e83be8fcebbb8110a59f5929e77f96](https://github.com/user-attachments/assets/0b41c79d-5a42-4136-ae2e-a4c5c37b5520)
![8d8919fb3dba32585d0e2e01d4378df0](https://github.com/user-attachments/assets/a2a7c83b-ab16-430a-92ed-2c71877d86a3)
![9c083e6f3509c0741c710f0140f08ae7](https://github.com/user-attachments/assets/91be6aaf-b1c0-4f06-a19b-ef713526a132)
![01b260ee29663d9f5e0236636785404e](https://github.com/user-attachments/assets/5cb79c3b-beaa-4fe6-af98-a2dc593ed79c)
![032c2c61fd1e51511bf03a83aae71e10](https://github.com/user-attachments/assets/e00a6d37-e086-42a0-92ac-028ad7e6298c)


## 🏗 Project Architecture

### Web Application Structure
```
EXAM-MASTER/
├── app.py                 # Main Flask application
├── database.db           # SQLite database
├── questions.csv         # Question bank data
├── requirements.txt      # Python dependencies
├── static/              # CSS and static files
├── templates/           # Jinja2 HTML templates
└── tools/               # Data conversion utilities
```

### Android Application Structure
```
ExamMasterAndroid/
├── app/src/main/kotlin/com/exammaster/
│   ├── data/            # Data layer (Room, Repository)
│   ├── di/              # Dependency injection (Hilt)
│   ├── ui/              # UI layer (Compose screens)
│   └── MainActivity.kt  # Entry point
└── build.gradle.kts     # Build configuration
```

## 🔧 Development Tools

### Question Conversion Tools
The project includes tools for converting questions from various formats:

- `tools/convert_txt_csv.py` - Convert text format to CSV
- `tools/convert_gongtongt_txt_to_csv.py` - Convert specialized formats

Example usage:
```bash
python tools/convert_txt_csv.py input.txt output.csv
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 👥 Author

- **Developer**: ShayneChen
- **Email**: [xinyu-c@outlook.com](mailto:xinyu-c@outlook.com)
- **GitHub**: [CiE-XinYuChen](https://github.com/CiE-XinYuChen)
- **Project Homepage**: [EXAM-MASTER](https://github.com/CiE-XinYuChen/EXAM-MASTER)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Material Design 3 for design guidelines
- Jetpack Compose community for UI components
- Flask community for web framework support
- All contributors and users of this project

---

⭐ **If you find this project helpful, please give it a star!**

Feel free to submit issues or pull requests to help improve the system!
