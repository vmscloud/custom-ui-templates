import path from 'path';
import fs from 'fs';
import options from './config/license.config.js';

// function _checkLicense(e,t,s){let i=exports.culture.Licensing||_licStr,n=null;s?_checkExpiration(e,s)?_checkVersion(e,s)?_checkDomain(e,s)?_checkProductCode(e,s)?_checkEval(e,s)&&(n=i.evl):n=i.prd:n=i.dmn:n=i.ver:n=i.exp:n=t?i.lic:i.mss;n&&_addWme(e,n+="<br/><br/>"+i.ctc,s)}

function main() {
  const cwd = process.cwd();
  // remove cache
  options.cacheDirs.forEach((cacheDir) => {
    const cachePath = path.join(cwd, cacheDir);
    if (!fs.existsSync(cachePath)) return;
    fs.rmSync(cachePath, { recursive: true, force: true });
    console.info(`remove cache folder => ${cachePath}`);
  });
  // change code
  options.distDirs.forEach((distDir) => {
    const distPath = path.join(cwd, distDir);
    if (!fs.existsSync(distPath)) return;
    const dirs = fs.readdirSync(distPath);
    if (!dirs || dirs.length === 0) return;
    dirs.forEach((fileName) => {
      if (!fileName.endsWith('js')) return;
      const filePath = path.join(distPath, fileName);
      const contents = fs.readFileSync(filePath, {
        encoding: 'utf8',
        flag: 'r',
      });

      const regexp = new RegExp(
        'function _checkLicense\\(([a-z,])*\\){([A-Za-z \\{\\}\\[\\]\\/?.,;:|\\)*~`!^\\-_+<>@%&\\\\=\\(\\\'\\")])*}',
        'g',
      );
      const to = `function _checkLicense(e,t,s){}`;
      if (contents.match(regexp)) {
        fs.writeFileSync(filePath, contents.replace(regexp, to), 'utf8');
        console.info(`change files => ${filePath}`);
      }
    });
  });
}

main();
