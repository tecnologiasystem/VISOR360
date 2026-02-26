// vite.config.js
import { defineConfig } from "file:///C:/Users/j.castillo/Pictures/QA/QA/FE/node_modules/vite/dist/node/index.js";
import react from "file:///C:/Users/j.castillo/Pictures/QA/QA/FE/node_modules/@vitejs/plugin-react/dist/index.js";
import legacy from "file:///C:/Users/j.castillo/Pictures/QA/QA/FE/node_modules/@vitejs/plugin-legacy/dist/index.mjs";
var vite_config_default = defineConfig({
  plugins: [
    react(),
    legacy({
      targets: ["defaults", "safari >= 12", "iOS >= 12"],
      additionalLegacyPolyfills: ["regenerator-runtime/runtime"],
      renderLegacyChunks: true,
      polyfills: [
        "es.array.iterator",
        "es.promise",
        "es.object.assign",
        "es.promise.finally"
      ]
    })
  ],
  build: {
    target: ["es2015", "safari12"],
    cssTarget: ["safari12"]
  },
  server: {
    host: "0.0.0.0",
    // Exponer en toda la red
    port: 5175,
    // Proxy para desarrollo - en producción IIS maneja esto
    proxy: {
      "/api": {
        target: "http://localhost:8001",
        changeOrigin: true,
        secure: false
        // No reescribir la ruta, el BE ya espera /api
        // rewrite: (path) => path.replace(/^\/api/, '/api'),
      }
    }
  }
});
export {
  vite_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcuanMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCJDOlxcXFxVc2Vyc1xcXFxqLmNhc3RpbGxvXFxcXFBpY3R1cmVzXFxcXFFBXFxcXFFBXFxcXEZFXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ZpbGVuYW1lID0gXCJDOlxcXFxVc2Vyc1xcXFxqLmNhc3RpbGxvXFxcXFBpY3R1cmVzXFxcXFFBXFxcXFFBXFxcXEZFXFxcXHZpdGUuY29uZmlnLmpzXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ltcG9ydF9tZXRhX3VybCA9IFwiZmlsZTovLy9DOi9Vc2Vycy9qLmNhc3RpbGxvL1BpY3R1cmVzL1FBL1FBL0ZFL3ZpdGUuY29uZmlnLmpzXCI7aW1wb3J0IHsgZGVmaW5lQ29uZmlnIH0gZnJvbSAndml0ZSdcclxuaW1wb3J0IHJlYWN0IGZyb20gJ0B2aXRlanMvcGx1Z2luLXJlYWN0J1xyXG5pbXBvcnQgbGVnYWN5IGZyb20gJ0B2aXRlanMvcGx1Z2luLWxlZ2FjeSdcclxuXHJcbi8vIGh0dHBzOi8vdml0ZWpzLmRldi9jb25maWcvXHJcbmV4cG9ydCBkZWZhdWx0IGRlZmluZUNvbmZpZyh7XHJcbiAgcGx1Z2luczogW1xyXG4gICAgcmVhY3QoKSxcclxuICAgIGxlZ2FjeSh7XHJcbiAgICAgIHRhcmdldHM6IFsnZGVmYXVsdHMnLCAnc2FmYXJpID49IDEyJywgJ2lPUyA+PSAxMiddLFxyXG4gICAgICBhZGRpdGlvbmFsTGVnYWN5UG9seWZpbGxzOiBbJ3JlZ2VuZXJhdG9yLXJ1bnRpbWUvcnVudGltZSddLFxyXG4gICAgICByZW5kZXJMZWdhY3lDaHVua3M6IHRydWUsXHJcbiAgICAgIHBvbHlmaWxsczogW1xyXG4gICAgICAgICdlcy5hcnJheS5pdGVyYXRvcicsXHJcbiAgICAgICAgJ2VzLnByb21pc2UnLFxyXG4gICAgICAgICdlcy5vYmplY3QuYXNzaWduJyxcclxuICAgICAgICAnZXMucHJvbWlzZS5maW5hbGx5J1xyXG4gICAgICBdXHJcbiAgICB9KVxyXG4gIF0sXHJcbiAgYnVpbGQ6IHtcclxuICAgIHRhcmdldDogWydlczIwMTUnLCAnc2FmYXJpMTInXSxcclxuICAgIGNzc1RhcmdldDogWydzYWZhcmkxMiddXHJcbiAgfSxcclxuICBzZXJ2ZXI6IHtcclxuICAgIGhvc3Q6ICcwLjAuMC4wJywgLy8gRXhwb25lciBlbiB0b2RhIGxhIHJlZFxyXG4gICAgcG9ydDogNTE3NSxcclxuICAgIC8vIFByb3h5IHBhcmEgZGVzYXJyb2xsbyAtIGVuIHByb2R1Y2NpXHUwMEYzbiBJSVMgbWFuZWphIGVzdG9cclxuICAgIHByb3h5OiB7XHJcbiAgICAgICcvYXBpJzoge1xyXG4gICAgICAgIHRhcmdldDogJ2h0dHA6Ly9sb2NhbGhvc3Q6ODAwMScsXHJcbiAgICAgICAgY2hhbmdlT3JpZ2luOiB0cnVlLFxyXG4gICAgICAgIHNlY3VyZTogZmFsc2UsXHJcbiAgICAgICAgLy8gTm8gcmVlc2NyaWJpciBsYSBydXRhLCBlbCBCRSB5YSBlc3BlcmEgL2FwaVxyXG4gICAgICAgIC8vIHJld3JpdGU6IChwYXRoKSA9PiBwYXRoLnJlcGxhY2UoL15cXC9hcGkvLCAnL2FwaScpLFxyXG4gICAgICB9XHJcbiAgICB9XHJcbiAgfVxyXG59KVxyXG4iXSwKICAibWFwcGluZ3MiOiAiO0FBQStTLFNBQVMsb0JBQW9CO0FBQzVVLE9BQU8sV0FBVztBQUNsQixPQUFPLFlBQVk7QUFHbkIsSUFBTyxzQkFBUSxhQUFhO0FBQUEsRUFDMUIsU0FBUztBQUFBLElBQ1AsTUFBTTtBQUFBLElBQ04sT0FBTztBQUFBLE1BQ0wsU0FBUyxDQUFDLFlBQVksZ0JBQWdCLFdBQVc7QUFBQSxNQUNqRCwyQkFBMkIsQ0FBQyw2QkFBNkI7QUFBQSxNQUN6RCxvQkFBb0I7QUFBQSxNQUNwQixXQUFXO0FBQUEsUUFDVDtBQUFBLFFBQ0E7QUFBQSxRQUNBO0FBQUEsUUFDQTtBQUFBLE1BQ0Y7QUFBQSxJQUNGLENBQUM7QUFBQSxFQUNIO0FBQUEsRUFDQSxPQUFPO0FBQUEsSUFDTCxRQUFRLENBQUMsVUFBVSxVQUFVO0FBQUEsSUFDN0IsV0FBVyxDQUFDLFVBQVU7QUFBQSxFQUN4QjtBQUFBLEVBQ0EsUUFBUTtBQUFBLElBQ04sTUFBTTtBQUFBO0FBQUEsSUFDTixNQUFNO0FBQUE7QUFBQSxJQUVOLE9BQU87QUFBQSxNQUNMLFFBQVE7QUFBQSxRQUNOLFFBQVE7QUFBQSxRQUNSLGNBQWM7QUFBQSxRQUNkLFFBQVE7QUFBQTtBQUFBO0FBQUEsTUFHVjtBQUFBLElBQ0Y7QUFBQSxFQUNGO0FBQ0YsQ0FBQzsiLAogICJuYW1lcyI6IFtdCn0K
