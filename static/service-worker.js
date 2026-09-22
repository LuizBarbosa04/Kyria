const CACHE_NAME = "kyria-pwa-v1"

const APP_SHELL = [
    "/",
    "/static/manifest.webmanifest",
    "/static/icons/kyria-192.png",
    "/static/icons/kyria-512.png"
]

self.addEventListener("install", function(evento) {
    evento.waitUntil(
        caches.open(CACHE_NAME).then(function(cache) {
            return cache.addAll(APP_SHELL)
        })
    )
})

self.addEventListener("activate", function(evento) {
    evento.waitUntil(
        caches.keys().then(function(chaves) {
            return Promise.all(
                chaves
                    .filter(function(chave) {
                        return chave !== CACHE_NAME
                    })
                    .map(function(chave) {
                        return caches.delete(chave)
                    })
            )
        })
    )
})

self.addEventListener("fetch", function(evento) {
    const url = new URL(evento.request.url)

    if (evento.request.method !== "GET" || url.origin !== self.location.origin) {
        return
    }

    if (!APP_SHELL.includes(url.pathname)) {
        return
    }

    evento.respondWith(
        fetch(evento.request)
            .then(function(resposta) {
                const copia = resposta.clone()

                caches.open(CACHE_NAME).then(function(cache) {
                    cache.put(evento.request, copia)
                })

                return resposta
            })
            .catch(function() {
                return caches.match(evento.request)
            })
    )
})
