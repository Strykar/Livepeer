function clean_lpt_logs() {
    grep -vE "http: TLS handshake error from|block_watcher\.go:[0-9]+] Polling blocks from=" "$@"
}
