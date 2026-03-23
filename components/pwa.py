import streamlit as st
import streamlit.components.v1 as components

def render_pwa():
    pwa_html = """
    <script>
      // Register Service Worker
      if ('serviceWorker' in navigator) {
        window.addEventListener('load', function() {
          navigator.serviceWorker.register('/app/static/service-worker.js').then(function(registration) {
            console.log('ServiceWorker registration successful with scope: ', registration.scope);
          }, function(err) {
            console.log('ServiceWorker registration failed: ', err);
          });
        });
      }

      // Inject Manifest Link
      const manifestNode = document.createElement('link');
      manifestNode.rel = 'manifest';
      manifestNode.href = '/app/static/manifest.json';
      document.head.appendChild(manifestNode);

      // Inject Theme Color
      const themeNode = document.createElement('meta');
      themeNode.name = 'theme-color';
      themeNode.content = '#1e1e2e';
      document.head.appendChild(themeNode);

      // Inject Apple Touch Icon
      const appleIconNode = document.createElement('link');
      appleIconNode.rel = 'apple-touch-icon';
      appleIconNode.href = '/app/static/icon-192.png';
      document.head.appendChild(appleIconNode);
      
      console.log("PWA attributes injected successfully!");
    </script>
    """
    components.html(pwa_html, height=0, width=0)
