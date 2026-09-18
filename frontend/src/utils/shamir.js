// Nativní implementace Shamir's Secret Sharing pro prohlížeče
const logs = [], exps = [];
let x = 1;
for (let i = 0; i < 256; i++) {
    exps[i] = x;
    logs[x] = i;
    x <<= 1;
    if (x & 256) x ^= 0x11d; // GF(2^8) s polynomem 0x11d
}

const add = (a, b) => a ^ b;
const mul = (a, b) => (a === 0 || b === 0) ? 0 : exps[(logs[a] + logs[b]) % 255];

const evalPoly = (poly, x) => {
    let y = 0;
    for (let i = poly.length - 1; i >= 0; i--) {
        y = add(mul(y, x), poly[i]);
    }
    return y;
};

export const splitSecret = (secretHex, sharesCount, threshold) => {
    const secret = secretHex.match(/.{1,2}/g).map(byte => parseInt(byte, 16));
    const shares = Array.from({ length: sharesCount }, () => []);
    
    for (let i = 0; i < secret.length; i++) {
        const poly = [secret[i]];
        for (let j = 1; j < threshold; j++) {
            const randomByte = new Uint8Array(1);
            window.crypto.getRandomValues(randomByte);
            poly.push(randomByte[0]);
        }
        
        for (let px = 1; px <= sharesCount; px++) {
            shares[px - 1].push(evalPoly(poly, px));
        }
    }
    
    return shares.map((share, idx) => {
        const xHex = (idx + 1).toString(16).padStart(2, '0');
        const yHex = share.map(b => b.toString(16).padStart(2, '0')).join('');
        return xHex + yHex;
    });
};

export const stringToHex = (str) => {
    return Array.from(new TextEncoder().encode(str))
        .map(b => b.toString(16).padStart(2, '0')).join('');
};
