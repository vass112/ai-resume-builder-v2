const VALID_REDEEM_CODES = ['TEST10', 'FREE3', 'DEV2024', 'PREMIUM', 'BETA'];

export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { code } = req.body;
  if (!code) {
    return res.status(400).json({ error: 'Code is required' });
  }

  const normalized = code.trim().toUpperCase();
  const isValid = VALID_REDEEM_CODES.includes(normalized);

  if (!isValid) {
    return res.status(200).json({ valid: false, message: 'Invalid code' });
  }

  return res.status(200).json({ valid: true, message: 'Code accepted! 3 downloads added', credits: 3 });
}
