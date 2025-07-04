import { defineConfig } from 'sanity';
import { structureTool } from 'sanity/structure';
import { visionTool } from '@sanity/vision';
import { schemaTypes } from './schemas';
import { structure, defaultDocumentNodeResolver } from './src/structure.jsx';

export default defineConfig({
  name: 'default',
  title: 'Rental Village Content Management',

  projectId: '2pxuaj9k',
  dataset: 'production',

  plugins: [
    structureTool({
      structure,
      defaultDocumentNode: defaultDocumentNodeResolver,
    }),
    visionTool()
  ],

  schema: {
    types: schemaTypes,
  },
});