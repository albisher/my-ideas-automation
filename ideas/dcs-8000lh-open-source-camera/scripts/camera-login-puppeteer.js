const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

// Camera configuration
const CAMERA_IP = '192.168.68.1';
const CAMERA_URL = `http://${CAMERA_IP}`;
const SCREENSHOT_DIR = '/Users/amac/myIdeas/ideas/dcs-8000lh-open-source-camera/screenshots';

// Login credentials to try
const LOGIN_CREDENTIALS = [
    { username: 'admin', password: 'admin' },
    { username: 'admin', password: '052446' },
    { username: 'admin', password: 'password' },
    { username: 'admin', password: '12345' },
    { username: 'root', password: 'admin' },
    { username: 'user', password: 'user' },
    { username: '', password: '' }, // Try no credentials
];

async function loginToCamera() {
    console.log('🔐 Logging into DCS-8000LH Camera');
    console.log('=' * 60);
    console.log(`Camera IP: ${CAMERA_IP}`);
    console.log(`Camera URL: ${CAMERA_URL}`);
    console.log('');

    const browser = await puppeteer.launch({
        headless: false,
        defaultViewport: { width: 1280, height: 720 },
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });

    try {
        const page = await browser.newPage();
        
        // Set user agent
        await page.setUserAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36');
        
        console.log('🌐 Accessing camera login page...');
        await page.goto(CAMERA_URL, { waitUntil: 'networkidle2', timeout: 10000 });
        
        // Take screenshot of login page
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const loginScreenshot = path.join(SCREENSHOT_DIR, `camera-login-${timestamp}.png`);
        await page.screenshot({ path: loginScreenshot, fullPage: true });
        console.log(`📸 Login page screenshot: ${loginScreenshot}`);
        
        // Try to find login form elements
        console.log('🔍 Looking for login form elements...');
        
        // Common login form selectors
        const usernameSelectors = [
            'input[name="username"]',
            'input[name="user"]',
            'input[name="login"]',
            'input[name="userid"]',
            'input[type="text"]',
            'input[id="username"]',
            'input[id="user"]',
            '#username',
            '#user',
            '#login'
        ];
        
        const passwordSelectors = [
            'input[name="password"]',
            'input[name="pass"]',
            'input[type="password"]',
            'input[id="password"]',
            'input[id="pass"]',
            '#password',
            '#pass'
        ];
        
        const submitSelectors = [
            'input[type="submit"]',
            'button[type="submit"]',
            'button',
            'input[value="Login"]',
            'input[value="Submit"]',
            'input[value="OK"]',
            '#login',
            '#submit',
            '#ok'
        ];
        
        let usernameField = null;
        let passwordField = null;
        let submitButton = null;
        
        // Find username field
        for (const selector of usernameSelectors) {
            try {
                usernameField = await page.$(selector);
                if (usernameField) {
                    console.log(`✅ Found username field: ${selector}`);
                    break;
                }
            } catch (e) {
                // Continue to next selector
            }
        }
        
        // Find password field
        for (const selector of passwordSelectors) {
            try {
                passwordField = await page.$(selector);
                if (passwordField) {
                    console.log(`✅ Found password field: ${selector}`);
                    break;
                }
            } catch (e) {
                // Continue to next selector
            }
        }
        
        // Find submit button
        for (const selector of submitSelectors) {
            try {
                submitButton = await page.$(selector);
                if (submitButton) {
                    console.log(`✅ Found submit button: ${selector}`);
                    break;
                }
            } catch (e) {
                // Continue to next selector
            }
        }
        
        if (!usernameField || !passwordField || !submitButton) {
            console.log('❌ Could not find login form elements');
            console.log('📄 Page content preview:');
            const content = await page.content();
            console.log(content.substring(0, 1000));
            return;
        }
        
        // Try different login credentials
        for (const creds of LOGIN_CREDENTIALS) {
            console.log(`🔐 Trying login: ${creds.username} / ${creds.password}`);
            
            try {
                // Clear and fill username
                await usernameField.click({ clickCount: 3 });
                await usernameField.type(creds.username);
                
                // Clear and fill password
                await passwordField.click({ clickCount: 3 });
                await passwordField.type(creds.password);
                
                // Take screenshot before login
                const beforeLoginScreenshot = path.join(SCREENSHOT_DIR, `camera-before-login-${creds.username}-${timestamp}.png`);
                await page.screenshot({ path: beforeLoginScreenshot, fullPage: true });
                console.log(`📸 Before login screenshot: ${beforeLoginScreenshot}`);
                
                // Submit form
                await submitButton.click();
                
                // Wait for navigation or response
                await page.waitForTimeout(3000);
                
                // Check if login was successful
                const currentUrl = page.url();
                const pageTitle = await page.title();
                
                console.log(`📄 Current URL: ${currentUrl}`);
                console.log(`📄 Page title: ${pageTitle}`);
                
                // Take screenshot after login attempt
                const afterLoginScreenshot = path.join(SCREENSHOT_DIR, `camera-after-login-${creds.username}-${timestamp}.png`);
                await page.screenshot({ path: afterLoginScreenshot, fullPage: true });
                console.log(`📸 After login screenshot: ${afterLoginScreenshot}`);
                
                // Check for success indicators
                if (currentUrl !== CAMERA_URL || 
                    pageTitle.toLowerCase().includes('main') ||
                    pageTitle.toLowerCase().includes('dashboard') ||
                    pageTitle.toLowerCase().includes('control') ||
                    pageTitle.toLowerCase().includes('admin')) {
                    console.log(`✅ Login successful with: ${creds.username} / ${creds.password}`);
                    
                    // Now try to find streaming settings
                    console.log('🎥 Looking for streaming settings...');
                    await findStreamingSettings(page, timestamp);
                    
                    return;
                } else {
                    console.log(`❌ Login failed with: ${creds.username} / ${creds.password}`);
                }
                
            } catch (error) {
                console.log(`❌ Error during login attempt: ${error.message}`);
            }
        }
        
        console.log('❌ All login attempts failed');
        
    } catch (error) {
        console.error('❌ Error during camera login:', error);
    } finally {
        await browser.close();
    }
}

async function findStreamingSettings(page, timestamp) {
    console.log('🔍 Looking for streaming settings...');
    
    // Look for common streaming-related elements
    const streamingSelectors = [
        'a[href*="video"]',
        'a[href*="stream"]',
        'a[href*="live"]',
        'a[href*="camera"]',
        'button[onclick*="stream"]',
        'button[onclick*="video"]',
        'input[value*="stream"]',
        'input[value*="video"]'
    ];
    
    for (const selector of streamingSelectors) {
        try {
            const element = await page.$(selector);
            if (element) {
                console.log(`✅ Found streaming element: ${selector}`);
                
                // Take screenshot of streaming element
                const streamingScreenshot = path.join(SCREENSHOT_DIR, `camera-streaming-element-${timestamp}.png`);
                await page.screenshot({ path: streamingScreenshot, fullPage: true });
                console.log(`📸 Streaming element screenshot: ${streamingScreenshot}`);
                
                // Try to click the element
                await element.click();
                await page.waitForTimeout(2000);
                
                // Take screenshot after clicking
                const afterClickScreenshot = path.join(SCREENSHOT_DIR, `camera-after-click-${timestamp}.png`);
                await page.screenshot({ path: afterClickScreenshot, fullPage: true });
                console.log(`📸 After click screenshot: ${afterClickScreenshot}`);
            }
        } catch (e) {
            // Continue to next selector
        }
    }
    
    // Try to access common streaming URLs
    const streamingUrls = [
        '/video/mpegts.cgi',
        '/mjpg/video.cgi',
        '/snapshot.jpg',
        '/image.jpg',
        '/video.cgi',
        '/stream.cgi',
        '/live',
        '/stream'
    ];
    
    for (const url of streamingUrls) {
        try {
            console.log(`🎬 Testing streaming URL: ${url}`);
            const response = await page.goto(`${CAMERA_IP}${url}`, { 
                waitUntil: 'networkidle2', 
                timeout: 5000 
            });
            
            if (response && response.status() === 200) {
                console.log(`✅ Streaming URL working: ${url}`);
                
                // Take screenshot of working streaming URL
                const streamingUrlScreenshot = path.join(SCREENSHOT_DIR, `camera-streaming-url-${url.replace(/[\/]/g, '-')}-${timestamp}.png`);
                await page.screenshot({ path: streamingUrlScreenshot, fullPage: true });
                console.log(`📸 Streaming URL screenshot: ${streamingUrlScreenshot}`);
            }
        } catch (error) {
            console.log(`❌ Streaming URL not working: ${url}`);
        }
    }
}

// Run the login test
loginToCamera().catch(console.error);
