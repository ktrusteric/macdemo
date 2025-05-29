// 前端页面加载测试脚本
const puppeteer = require('puppeteer');

async function testFrontendPages() {
  const browser = await puppeteer.launch({ 
    headless: false,
    defaultViewport: { width: 1280, height: 800 }
  });
  
  const page = await browser.newPage();
  
  const testResults = [];
  
  // 测试页面列表
  const pagesToTest = [
    { name: 'Login', url: 'http://localhost:5173/login' },
    { name: 'Register', url: 'http://localhost:5173/register' },
    { name: 'Dashboard', url: 'http://localhost:5173/' },
    { name: 'Tags Management', url: 'http://localhost:5173/tags' },
    { name: 'Content List', url: 'http://localhost:5173/content' },
    { name: 'AI Assistants', url: 'http://localhost:5173/ai-assistants' },
    { name: 'Settings', url: 'http://localhost:5173/settings' },
    { name: 'Research Reports', url: 'http://localhost:5173/research' }
  ];
  
  console.log('🚀 开始前端页面测试...\n');
  
  for (const testPage of pagesToTest) {
    try {
      console.log(`📄 测试页面: ${testPage.name}`);
      
      // 导航到页面
      await page.goto(testPage.url, { waitUntil: 'networkidle0', timeout: 10000 });
      
      // 等待页面加载
      await page.waitForTimeout(2000);
      
      // 检查页面标题
      const title = await page.title();
      
      // 检查是否有React错误
      const reactErrors = await page.evaluate(() => {
        return window.console && window.console.error ? 
          window.console.error.toString() : null;
      });
      
      // 检查页面内容是否存在
      const hasContent = await page.evaluate(() => {
        const content = document.querySelector('#root');
        return content && content.textContent.trim().length > 0;
      });
      
      // 截图
      await page.screenshot({ 
        path: `screenshot_${testPage.name.replace(/\s+/g, '_')}.png`,
        fullPage: true 
      });
      
      const result = {
        name: testPage.name,
        url: testPage.url,
        title,
        hasContent,
        status: hasContent ? '✅ 成功' : '❌ 空白',
        screenshot: `screenshot_${testPage.name.replace(/\s+/g, '_')}.png`
      };
      
      testResults.push(result);
      console.log(`   状态: ${result.status}`);
      console.log(`   标题: ${title}`);
      
    } catch (error) {
      console.log(`   ❌ 错误: ${error.message}`);
      testResults.push({
        name: testPage.name,
        url: testPage.url,
        status: '❌ 错误',
        error: error.message
      });
    }
    
    console.log('');
  }
  
  // 输出测试报告
  console.log('📊 测试报告:');
  console.log('=' * 50);
  
  testResults.forEach(result => {
    console.log(`${result.name}: ${result.status}`);
    if (result.title) console.log(`  标题: ${result.title}`);
    if (result.error) console.log(`  错误: ${result.error}`);
  });
  
  await browser.close();
}

// 运行测试
testFrontendPages().catch(console.error); 