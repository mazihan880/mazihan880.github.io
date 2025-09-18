# Personal Academic Homepage

A modern, responsive personal homepage designed for academics and researchers. This template is inspired by clean academic websites and optimized for easy maintenance and GitHub Pages hosting.

## 🌟 Features

- **Clean, Modern Design**: Professional academic layout with smooth animations
- **Responsive**: Works perfectly on desktop, tablet, and mobile devices
- **Publications Management**: Automatic highlighting of first-author papers
- **Easy Maintenance**: Simple configuration through JavaScript data objects
- **GitHub Pages Ready**: Zero-configuration deployment
- **SEO Optimized**: Meta tags and structured data for better search visibility
- **Interactive Elements**: Smooth scrolling, hover effects, and copy-to-clipboard functionality

## 🚀 Quick Setup

### 1. Fork and Clone
1. Fork this repository to your GitHub account
2. Rename the repository to `yourusername.github.io`
3. Clone to your local machine:
   ```bash
   git clone https://github.com/yourusername/yourusername.github.io.git
   cd yourusername.github.io
   ```

### 2. Customize Your Information

#### Basic Information (index.html)
Update the following sections in `index.html`:
- **Name and Title**: Replace "Your Name" and position information
- **Contact Links**: Update email, Google Scholar, GitHub, Twitter links
- **About Section**: Add your personal introduction
- **Research Interests**: List your research areas
- **News Section**: Add recent updates and achievements
- **Education**: Add your educational background
- **Experience**: Add your work experience

#### Publications (script.js)
Update the `publications` object in `script.js`:
```javascript
const publications = {
    firstAuthor: [
        {
            title: "Your Paper Title",
            authors: "Your Name, Co-author 1, Co-author 2",
            venue: "Conference/Journal Name, Year",
            links: [
                { text: "Paper", url: "link-to-paper" },
                { text: "Code", url: "link-to-code" },
                { text: "Demo", url: "link-to-demo" }
            ]
        }
        // Add more publications...
    ],
    coAuthor: [
        // Add co-authored publications...
    ]
};
```

#### Profile Image
Replace `profile.svg` with your actual photo:
- Recommended size: 180x180 pixels
- Supported formats: JPG, PNG, SVG
- Update the `src` attribute in `index.html` if using a different filename

#### Site Configuration (_config.yml)
Update GitHub Pages settings:
- Change `title`, `description`, and `url`
- Update social media links
- Modify SEO settings

### 3. Deploy to GitHub Pages
1. Push your changes to the main branch:
   ```bash
   git add .
   git commit -m "Initial setup of personal homepage"
   git push origin main
   ```
2. Go to your repository settings on GitHub
3. Navigate to "Pages" section
4. Select "Deploy from a branch" and choose "main"
5. Your site will be available at `https://yourusername.github.io`

## 📝 Maintenance Guide

### Adding New Publications
1. Open `script.js`
2. Add new publication objects to the appropriate array (`firstAuthor` or `coAuthor`)
3. Include all relevant links (paper, code, demo, etc.)
4. Commit and push changes

### Updating Personal Information
- **Basic info**: Edit `index.html` directly
- **Styling**: Modify `styles.css` for visual changes
- **Functionality**: Update `script.js` for interactive features

### Customizing Design
The website uses CSS custom properties for easy theming. Key color variables are defined in `styles.css`:
- Primary colors: `#3498db`, `#2c3e50`
- Accent colors: `#e74c3c`, `#9b59b6`
- Background: `#fafafa`, `#f8f9fa`

## 🎨 Customization Options

### Color Scheme
Modify the CSS variables in `styles.css` to change the color scheme:
```css
:root {
    --primary-color: #3498db;
    --secondary-color: #2c3e50;
    --accent-color: #e74c3c;
    --background-color: #fafafa;
}
```

### Layout Modifications
- **Container width**: Adjust `.container max-width` in CSS
- **Section spacing**: Modify margins in `.section` class
- **Typography**: Change font families and sizes

### Adding New Sections
1. Add HTML structure in `index.html`
2. Style the new section in `styles.css`
3. Add any interactive functionality in `script.js`

## 📱 Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## 🔧 Technical Details

### File Structure
```
├── index.html          # Main HTML file
├── styles.css          # CSS styling
├── script.js           # JavaScript functionality
├── profile.svg         # Profile image (replace with your photo)
├── _config.yml         # GitHub Pages configuration
└── README.md           # This file
```

### Dependencies
- **Fonts**: Inter from Google Fonts
- **Icons**: Font Awesome 6.0
- **No JavaScript frameworks**: Pure vanilla JS for better performance

### Performance Features
- Optimized images and SVG graphics
- Minimal external dependencies
- Efficient CSS with modern features
- Lazy loading and intersection observers

## 🤝 Contributing

Feel free to submit issues and enhancement requests! If you'd like to contribute:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

Design inspired by academic websites including:
- [Shudong Liu](https://sudanl.github.io/)
- [Chengyou Jia](https://chengyou-jia.github.io/)
- [Shangbin Feng](https://bunsenfeng.github.io/)

---

**Need help?** Open an issue or check the [GitHub Pages documentation](https://docs.github.com/en/pages).