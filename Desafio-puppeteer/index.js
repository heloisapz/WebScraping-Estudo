const pup = require('puppeteer');
const url = "https://www.adidas.com.br/calcados";
 
(async () => 
    {
  const browser = await pup.launch({ headless: false });
  const page = await browser.newPage();
 
  await page.goto(url);
 
  await page.waitForSelector('#glass-gdpr-default-consent-accept-button', { timeout: 10000 });
  await page.click('#glass-gdpr-default-consent-accept-button');
 
  await page.waitForSelector('.product-card_product-card-content___bjeq', { timeout: 10000 });
 
  const dados = await page.$$eval('.product-card_product-card-content___bjeq', (produtos) => 
    {
    return produtos.map((produto, index) => 
    {
      const nome = produto.querySelector('.product-card-description_name__xHvJ2')?.innerText || null;
      const preco = produto.querySelector('._priceComponent_1dbqy_14')?.innerText || null;
      const categoria = produto.querySelector('.product-card-description_info__z_CcT')?.innerText || null;
      const img = produto.querySelector('img')?.src || null;
 
      return {"Tênis de número " : index + 1, nome, preco, categoria, img};
    });
    });
 
  console.log(dados);
 
  await browser.close();
})();
 