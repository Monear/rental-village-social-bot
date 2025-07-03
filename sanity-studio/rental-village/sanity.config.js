import { defineConfig } from 'sanity';
import { structureTool } from 'sanity/structure';
import { visionTool } from '@sanity/vision';
import { schemaTypes } from './schemas';

export default defineConfig({
  name: 'default',
  title: 'Rental Village',

  projectId: '2pxuaj9k',
  dataset: 'production', // Replace with your dataset name

  plugins: [structureTool(), visionTool()],

  schema: {
    types: schemaTypes,
  },
});