const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

// Camera configuration
const CAMERA_IP = '192.168.68.1';
const CAMERA_URL = `http://${CAMERA_IP}`;
const SCREENSHOT_DIR = '/Users/amac/myIdeas/ideas/dcs-8000lh-open-source-camera/screenshots';

// Create screenshots directory if it doesn't exist
if (!fs.existsSync(SCREENSHOT_DIR)) {
    fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

async function testCamera() {
    console.log('🎥 Testing DCS-8000LH Camera with Puppeteer');
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
        
        console.log('🌐 Testing camera web interface...');
        
        // Test 1: Basic camera access
        console.log(`📱 Testing: ${CAMERA_URL}`);
        try {
            await page.goto(CAMERA_URL, { 
                waitUntil: 'networkidle2', 
                timeout: 10000 
            });
            
            // Take screenshot of main page
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            const screenshot1 = path.join(SCREENSHOT_DIR, `camera-main-${timestamp}.png`);
            await page.screenshot({ path: screenshot1, fullPage: true });
            console.log(`✅ Screenshot saved: ${screenshot1}`);
            
            // Get page title and content
            const title = await page.title();
            const content = await page.content();
            console.log(`📄 Page title: ${title}`);
            console.log(`📄 Content length: ${content.length} characters`);
            
        } catch (error) {
            console.log(`❌ Error accessing ${CAMERA_URL}: ${error.message}`);
        }
        
        // Test 2: Try common camera endpoints
        const endpoints = [
            '/common/info.cgi',
            '/config/',
            '/video/',
            '/cgi-bin/',
            '/admin/',
            '/login',
            '/index.html',
            '/main.html'
        ];
        
        for (const endpoint of endpoints) {
            const url = `${CAMERA_URL}${endpoint}`;
            console.log(`🔍 Testing: ${url}`);
            
            try {
                const response = await page.goto(url, { 
                    waitUntil: 'networkidle2', 
                    timeout: 5000 
                });
                
                if (response && response.status() === 200) {
                    console.log(`✅ Endpoint working: ${endpoint}`);
                    
                    // Take screenshot of working endpoint
                    const screenshot2 = path.join(SCREENSHOT_DIR, `camera-${endpoint.replace(/[\/]/g, '-')}-${timestamp}.png`);
                    await page.screenshot({ path: screenshot2, fullPage: true });
                    console.log(`📸 Screenshot saved: ${screenshot2}`);
                    
                    // Get content
                    const content = await page.content();
                    console.log(`📄 Content: ${content.substring(0, 200)}...`);
                } else {
                    console.log(`❌ Endpoint not working: ${endpoint}`);
                }
            } catch (error) {
                console.log(`❌ Error accessing ${endpoint}: ${error.message}`);
            }
        }
        
        // Test 3: Try streaming endpoints
        console.log('\n🎥 Testing streaming endpoints...');
        const streamingEndpoints = [
            '/video/mpegts.cgi',
            '/mjpg/video.cgi',
            '/snapshot.jpg',
            '/image.jpg',
            '/video.cgi',
            '/stream.cgi',
            '/live',
            '/stream'
        ];
        
        for (const endpoint of streamingEndpoints) {
            const url = `${CAMERA_URL}${endpoint}`;
            console.log(`🎬 Testing streaming: ${url}`);
            
            try {
                const response = await page.goto(url, { 
                    waitUntil: 'networkidle2', 
                    timeout: 5000 
                });
                
                if (response && response.status() === 200) {
                    console.log(`✅ Streaming endpoint working: ${endpoint}`);
                    
                    // Take screenshot of streaming endpoint
                    const screenshot3 = path.join(SCREENSHOT_DIR, `camera-streaming-${endpoint.replace(/[\/]/g, '-')}-${timestamp}.png`);
                    await page.screenshot({ path: screenshot3, fullPage: true });
                    console.log(`📸 Screenshot saved: ${screenshot3}`);
                } else {
                    console.log(`❌ Streaming endpoint not working: ${endpoint}`);
                }
            } catch (error) {
                console.log(`❌ Error accessing streaming ${endpoint}: ${error.message}`);
            }
        }
        
        // Test 4: Try different ports
        console.log('\n🔌 Testing different ports...');
        const ports = [80, 8080, 8081, 554, 1935, 8554];
        
        for (const port of ports) {
            const url = `http://${CAMERA_IP}:${port}`;
            console.log(`🔌 Testing port: ${url}`);
            
            try {
                const response = await page.goto(url, { 
                    waitUntil: 'networkidle2', 
                    timeout: 3000 
                });
                
                if (response && response.status() === 200) {
                    console.log(`✅ Port ${port} working!`);
                    
                    // Take screenshot of working port
                    const screenshot4 = path.join(SCREENSHOT_DIR, `camera-port-${port}-${timestamp}.png`);
                    await page.screenshot({ path: screenshot4, fullPage: true });
                    console.log(`📸 Screenshot saved: ${screenshot4}`);
                } else {
                    console.log(`❌ Port ${port} not working`);
                }
            } catch (error) {
                console.log(`❌ Error accessing port ${port}: ${error.message}`);
            }
        }
        
        console.log('\n✅ Camera testing completed!');
        console.log(`📁 Screenshots saved in: ${SCREENSHOT_DIR}`);
        
    } catch (error) {
        console.error('❌ Error during camera testing:', error);
    } finally {
        await browser.close();
    }
}

// Run the test
testCamera().catch(console.error);
