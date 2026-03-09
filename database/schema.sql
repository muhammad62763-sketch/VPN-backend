-- ── Enable UUID support ───────────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ── Users Table ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           TEXT UNIQUE NOT NULL,
    password_hash   TEXT NOT NULL,
    device_id       TEXT NOT NULL,
    role            TEXT NOT NULL DEFAULT 'user'
                    CHECK (role IN ('user', 'admin', 'superadmin')),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    is_banned       BOOLEAN NOT NULL DEFAULT FALSE,
    bandwidth_limit BIGINT DEFAULT 107374182400,  -- 100 GB in bytes; NULL = unlimited
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ── Refresh Tokens ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS refresh_tokens (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash  TEXT UNIQUE NOT NULL,
    is_revoked  BOOLEAN NOT NULL DEFAULT FALSE,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    expires_at  TIMESTAMPTZ NOT NULL
);

-- ── VPN Configs ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS vpn_configs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    config_id       TEXT UNIQUE NOT NULL,
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    client_ip       TEXT NOT NULL,
    preshared_key   TEXT NOT NULL,
    is_revoked      BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ── IP Pool (IPAM) ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ip_pool (
    id          SERIAL PRIMARY KEY,
    ip_address  TEXT UNIQUE NOT NULL,
    is_assigned BOOLEAN NOT NULL DEFAULT FALSE,
    user_id     UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Pre-fill 10.8.0.2 → 10.8.0.254
DO $$
BEGIN
    FOR i IN 2..254 LOOP
        INSERT INTO ip_pool (ip_address)
        VALUES ('10.8.0.' || i)
        ON CONFLICT DO NOTHING;
    END LOOP;
END $$;

-- ── Audit Logs (Admin visibility) ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS audit_logs (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_id    UUID REFERENCES users(id) ON DELETE SET NULL,
    action      TEXT NOT NULL,         -- e.g. 'ban_user', 'revoke_config'
    target_id   TEXT,                  -- user_id or config_id acted upon
    metadata    JSONB,
    ip_address  TEXT,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- ── VPN Servers (40-country pool) ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS vpn_servers (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    country         TEXT NOT NULL,
    country_code    TEXT NOT NULL,
    city            TEXT,
    endpoint        TEXT NOT NULL,
    public_key      TEXT NOT NULL,
    is_active       BOOLEAN DEFAULT TRUE,
    is_premium      BOOLEAN DEFAULT FALSE,
    load_percent    INT DEFAULT 0,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ── Indexes ───────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_users_email    ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role     ON users(role);
CREATE INDEX IF NOT EXISTS idx_rt_user_id     ON refresh_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_vpn_user_id    ON vpn_configs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_actor    ON audit_logs(actor_id);
CREATE INDEX IF NOT EXISTS idx_audit_created  ON audit_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_vpn_servers_country ON vpn_servers(country_code);
CREATE INDEX IF NOT EXISTS idx_vpn_servers_active  ON vpn_servers(is_active);

-- ── Seed first superadmin (change email/password via your app after) ──────────
INSERT INTO users (email, password_hash, device_id, role, bandwidth_limit)
VALUES (
    'admin@yourdomain.com',
    '$2b$12$CHANGE_THIS_HASH_AFTER_FIRST_LOGIN',  -- run hash_password() to replace
    'admin-device-seed',
    'superadmin',
    NULL   -- NULL = no bandwidth limit
) ON CONFLICT DO NOTHING;

-- ── Seed Sample VPN Servers ──────────────────────────────────────────────────
-- Add your actual servers after running setup script on each VPS
INSERT INTO vpn_servers (country, country_code, city, endpoint, public_key, is_premium) VALUES
('United States', 'US', 'Virginia',   'CHANGE_TO_YOUR_IP:51820', 'CHANGE_TO_SERVER_PUBKEY', FALSE),
('United Kingdom', 'GB', 'London',    'CHANGE_TO_YOUR_IP:51820', 'CHANGE_TO_SERVER_PUBKEY', FALSE),
('Germany',        'DE', 'Frankfurt', 'CHANGE_TO_YOUR_IP:51820', 'CHANGE_TO_SERVER_PUBKEY', FALSE),
('Japan',          'JP', 'Tokyo',     'CHANGE_TO_YOUR_IP:51820', 'CHANGE_TO_SERVER_PUBKEY', FALSE),
('Singapore',      'SG', 'Singapore', 'CHANGE_TO_YOUR_IP:51820', 'CHANGE_TO_SERVER_PUBKEY', FALSE),
('India',          'IN', 'Mumbai',    'CHANGE_TO_YOUR_IP:51820', 'CHANGE_TO_SERVER_PUBKEY', FALSE),
('UAE',            'AE', 'Dubai',     'CHANGE_TO_YOUR_IP:51820', 'CHANGE_TO_SERVER_PUBKEY', FALSE),
('Australia',      'AU', 'Sydney',    'CHANGE_TO_YOUR_IP:51820', 'CHANGE_TO_SERVER_PUBKEY', FALSE),
('Canada',         'CA', 'Toronto',   'CHANGE_TO_YOUR_IP:51820', 'CHANGE_TO_SERVER_PUBKEY', FALSE),
('Brazil',         'BR', 'São Paulo', 'CHANGE_TO_YOUR_IP:51820', 'CHANGE_TO_SERVER_PUBKEY', FALSE)
ON CONFLICT DO NOTHING;
