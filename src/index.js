
import Index from "./Index.svelte";

const app = new Index({
  target: document.body,
  props: {
     name: "Index",
  },
});

export default app;