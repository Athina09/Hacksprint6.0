/**
 * AES-256-GCM helpers (Web Crypto) — mirrors backend encryption for client-side field sealing.
 * Production secrets must only live in DATABASE_ENCRYPTION_KEY on the server.
 */

const ALGORITHM = "AES-256-GCM";
const IV_LENGTH = 12;
const KEY_LENGTH = 32;

export type EncryptedPayload = {
  v: 1;
  alg: typeof ALGORITHM;
  iv: string;
  ciphertext: string;
};

function bytesToBase64(bytes: Uint8Array): string {
  let binary = "";
  for (const b of bytes) binary += String.fromCharCode(b);
  return btoa(binary);
}

function base64ToBytes(encoded: string): Uint8Array {
  const binary = atob(encoded);
  const out = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) out[i] = binary.charCodeAt(i);
  return out;
}

async function deriveKey(secret: string): Promise<CryptoKey> {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(secret));
  return crypto.subtle.importKey("raw", digest, { name: ALGORITHM }, false, [
    "encrypt",
    "decrypt",
  ]);
}

export async function encryptString(
  plaintext: string,
  secret: string,
): Promise<EncryptedPayload> {
  const key = await deriveKey(secret);
  const iv = crypto.getRandomValues(new Uint8Array(IV_LENGTH));
  const ciphertext = await crypto.subtle.encrypt(
    { name: ALGORITHM, iv },
    key,
    new TextEncoder().encode(plaintext),
  );
  return {
    v: 1,
    alg: ALGORITHM,
    iv: bytesToBase64(iv),
    ciphertext: bytesToBase64(new Uint8Array(ciphertext)),
  };
}

export async function decryptString(
  payload: EncryptedPayload,
  secret: string,
): Promise<string> {
  if (payload.alg !== ALGORITHM || payload.v !== 1) {
    throw new Error("Unsupported encrypted payload");
  }
  const key = await deriveKey(secret);
  const plain = await crypto.subtle.decrypt(
    { name: ALGORITHM, iv: base64ToBytes(payload.iv) },
    key,
    base64ToBytes(payload.ciphertext),
  );
  return new TextDecoder().decode(plain);
}

export { ALGORITHM, KEY_LENGTH };
