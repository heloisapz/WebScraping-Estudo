//DESAFIO PUPPETEER - COLETA DE DADOS DO SITE ADIDAS
//Comentários no código foram feitos para fins didáticos e melhor compreensão do mesmo.

const pup = require('puppeteer'); //importando puppeteer
const fs = require('fs'); //importando fs (para manipulação do arquivo json)
const url = "https://www.adidas.com.br/calcados"; //URL do site a se coletar os dados

(async () => 
  {
  const browser = await pup.launch({ headless: false }); //inicia o puppeteer em modo não headless 
  // (assim, é possível ver o que está acontecendo no navegador)
  const page = await browser.newPage(); //abrindo uma nova aba no navegador
  await page.goto(url, { waitUntil: 'domcontentloaded' }); //navega até a URL especificada e espera o DOM carregar
  //waitUntil: 'domcontentloaded': Este parâmetro diz ao puppeteer para esperar 
  // até que o evento domcontentloaded seja disparado antes de continuar.

  //bloco de código para aceitar cookies do site da adidas
  //O botão de cookies pode não aparecer em todas as visitas,
  //então o código tenta clicar nele e, se não encontrar, ignora o erro (por isso o uso do try cath).
  try 
  {
    await page.waitForSelector('#glass-gdpr-default-consent-accept-button', { timeout: 10000 }); //espera o botão de cookies aparecer
    //timeout: 10000: este parâmetro diz ao puppeteer para esperar até 10 segundos
    await page.click('#glass-gdpr-default-consent-accept-button'); //clica no botão para aceitar os cookies (e fechar o modal)
  } 
  catch (e) 
  {
    console.log("Botão de cookies não encontrado ou já aceito."); 
  }

  let tenis = []; //array para armazenar os dados coletados
  //o array tenis será preenchido com os dados coletados de cada tênis encontrado na página.
  let pagina = 1; //variável para controlar o número da página atual

  while (true) //loop infinito para acessar todas as páginas de tênis
    {
    console.log(`Coletando dados da página ${pagina}...`);

    await page.waitForSelector('.product-card_product-card-content___bjeq', { timeout: 10000 }); 
    //espera o seletor dos tênis aparecer na página
    const dados = await page.$$eval('.product-card_product-card-content___bjeq', (lista) => { 
      //$$eval: avalia uma lista de elementos e retorna os dados desejados
      //lista: é a lista de elementos que foram encontrados com o seletor passado como parâmetro
      //a função de callback recebe a lista de elementos e retorna os dados desejados
      return lista.map((tenis) => {
        const nome = tenis.querySelector('.product-card-description_name__xHvJ2')?.innerText || null;
        const preco = tenis.querySelector('._priceComponent_1dbqy_14')?.innerText || null;
        const categoria = tenis.querySelector('.product-card-description_info__z_CcT')?.innerText || null;
        const img = tenis.querySelector('img')?.src || null;
        return { nome, preco, categoria, img };
      });
    });

    tenis.push(...dados); //adiciona os dados coletados no array dos tênis


    const btnmodal = await page.$('#gl-modal__close-mf-account-portal'); 
    //verifica se existe o botão de fechar modal (caso exista, clica nele)
    if (btnmodal) 
      {
      await btnmodal.click();
    }

    const botaoproximo = await page.$('a[data-testid="pagination-next-button"]'); //seleciona o botão de próxima página
    if (!botaoproximo) //verifica se o botão de próxima página existe
      {
      console.log("Botão 'Próxima página' não encontrado. Encerrando.");
      break;
    }

    await Promise.all([
      page.waitForNavigation({ waitUntil: 'domcontentloaded' }),
      //waitForNavigation: espera a navegação carregar antes de continuar
      botaoproximo.click(),
      //caso o botão de próxima página exista, clica nele e espera a navegação carregar
    ]);

    await new Promise(resolve => setTimeout(resolve, 1000));
    //espera 1 segundo para evitar quebra de requisições (para não sobrecarregar o servidor)

    pagina++;
  }

  fs.writeFileSync('tenis.json', JSON.stringify(tenis, null, 2), 'utf-8');
  //escreve os dados coletados no arquivo tenis.json (caso o arquivo não exista, ele será criado)
  console.log(`Foram coletados ${tenis.length} tênis em ${pagina} páginas.`);

  await browser.close();
  //fecha o navegador
})();
