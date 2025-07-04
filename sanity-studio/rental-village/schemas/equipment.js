// Corrected Equipment Schema - ALL original fields preserved, just organized in tabs
import { defineField, defineType } from 'sanity';

export default defineType({
  name: 'equipment',
  title: 'Equipment',
  type: 'document',
  groups: [
    {
      name: 'basic',
      title: 'Basic Info',
      default: true
    },
    {
      name: 'descriptions',
      title: 'Descriptions'
    },
    {
      name: 'media', 
      title: 'Media & Assets'
    },
    {
      name: 'pricing',
      title: 'Pricing & Availability'
    },
    {
      name: 'usecases',
      title: 'Use Cases & Industries'
    },
    {
      name: 'technical',
      title: 'Technical & Safety'
    },
    {
      name: 'seo',
      title: 'SEO & Content'
    },
    {
      name: 'ai',
      title: 'AI Generated'
    },
    {
      name: 'metadata',
      title: 'Metadata & Reviews'
    }
  ],
  fields: [
    // BASIC INFO TAB
    defineField({
      name: 'id',
      title: 'ID',
      type: 'string',
      validation: (Rule) => Rule.required(),
      group: 'basic'
    }),
    defineField({
      name: 'name',
      title: 'Name',
      type: 'string',
      validation: (Rule) => Rule.required(),
      group: 'basic'
    }),
    defineField({
      name: 'slug',
      title: 'Slug',
      type: 'slug',
      options: {
        source: 'name',
        maxLength: 96,
      },
      validation: (Rule) => Rule.required(),
      group: 'basic'
    }),
    defineField({
      name: 'brand',
      title: 'Brand',
      type: 'string',
      group: 'basic'
    }),
    defineField({
      name: 'model',
      title: 'Model',
      type: 'string',
      group: 'basic'
    }),
    defineField({
      name: 'categories',
      title: 'Categories',
      type: 'array',
      of: [{ type: 'string' }],
      group: 'basic'
    }),
    defineField({
      name: 'subcategories',
      title: 'Subcategories',
      type: 'array',
      of: [{ type: 'string' }],
      group: 'basic'
    }),

    // DESCRIPTIONS TAB
    defineField({
      name: 'short_description',
      title: 'Short Description',
      type: 'text',
      rows: 2,
      group: 'descriptions'
    }),
    defineField({
      name: 'full_description',
      title: 'Full Description',
      type: 'text',
      group: 'descriptions'
    }),
    defineField({
      name: 'technical_description',
      title: 'Technical Description',
      type: 'text',
      group: 'descriptions'
    }),

    // MEDIA & ASSETS TAB
    defineField({
      name: 'images',
      title: 'Images',
      type: 'array',
      of: [
        defineType({
          name: 'equipmentImage',
          title: 'Equipment Image',
          type: 'object',
          fields: [
            defineField({
              name: 'url',
              title: 'URL',
              type: 'url',
            }),
            defineField({
              name: 'alt_text',
              title: 'Alt Text',
              type: 'string',
            }),
            defineField({
              name: 'is_primary',
              title: 'Is Primary',
              type: 'boolean',
            }),
            defineField({
              name: 'size',
              title: 'Size',
              type: 'string',
            }),
          ],
        }),
      ],
      group: 'media'
    }),
    defineField({
      name: 'video_urls',
      title: 'Video URLs',
      type: 'array',
      of: [{ type: 'url' }],
      group: 'media'
    }),
    defineField({
      name: 'manual_urls',
      title: 'Manual URLs',
      type: 'array',
      of: [{ type: 'url' }],
      group: 'media'
    }),

    // PRICING & AVAILABILITY TAB
    defineField({
      name: 'pricing',
      title: 'Pricing',
      type: 'object',
      fields: [
        defineField({
          name: 'daily_rate',
          title: 'Daily Rate',
          type: 'number',
        }),
        defineField({
          name: 'weekly_rate',
          title: 'Weekly Rate',
          type: 'number',
        }),
        defineField({
          name: 'monthly_rate',
          title: 'Monthly Rate',
          type: 'number',
        }),
        defineField({
          name: 'currency',
          title: 'Currency',
          type: 'string',
        }),
        defineField({
          name: 'deposit_required',
          title: 'Deposit Required',
          type: 'number',
        }),
        defineField({
          name: 'minimum_rental_period',
          title: 'Minimum Rental Period',
          type: 'string',
        }),
      ],
      group: 'pricing'
    }),
    defineField({
      name: 'availability',
      title: 'Availability',
      type: 'object',
      fields: [
        defineField({
          name: 'status',
          title: 'Status',
          type: 'string',
          options: {
            list: ['available', 'unavailable', 'maintenance'],
          },
        }),
        defineField({
          name: 'quantity_available',
          title: 'Quantity Available',
          type: 'number',
        }),
      ],
      group: 'pricing'
    }),

    // USE CASES & INDUSTRIES TAB
    defineField({
      name: 'primary_use_cases',
      title: 'Primary Use Cases',
      type: 'array',
      of: [{ type: 'string' }],
      group: 'usecases'
    }),
    defineField({
      name: 'secondary_use_cases',
      title: 'Secondary Use Cases',
      type: 'array',
      of: [{ type: 'string' }],
      group: 'usecases'
    }),
    defineField({
      name: 'industries_served',
      title: 'Industries Served',
      type: 'array',
      of: [{ type: 'string' }],
      group: 'usecases'
    }),
    defineField({
      name: 'project_types',
      title: 'Project Types',
      type: 'array',
      of: [{ type: 'string' }],
      group: 'usecases'
    }),

    // TECHNICAL & SAFETY TAB
    defineField({
      name: 'specifications',
      title: 'Specifications',
      type: 'array',
      of: [
        defineType({
          name: 'specification',
          title: 'Specification',
          type: 'object',
          fields: [
            defineField({
              name: 'name',
              title: 'Name',
              type: 'string',
            }),
            defineField({
              name: 'value',
              title: 'Value',
              type: 'string',
            }),
            defineField({
              name: 'unit',
              title: 'Unit',
              type: 'string',
            }),
            defineField({
              name: 'category',
              title: 'Category',
              type: 'string',
            }),
          ],
        }),
      ],
      group: 'technical'
    }),
    defineField({
      name: 'power_source',
      title: 'Power Source',
      type: 'string',
      group: 'technical'
    }),
    defineField({
      name: 'weight',
      title: 'Weight',
      type: 'number',
      group: 'technical'
    }),
    defineField({
      name: 'safety',
      title: 'Safety',
      type: 'object',
      fields: [
        defineField({
          name: 'safety_requirements',
          title: 'Safety Requirements',
          type: 'array',
          of: [{ type: 'string' }],
        }),
        defineField({
          name: 'operator_certification_required',
          title: 'Operator Certification Required',
          type: 'boolean',
        }),
        defineField({
          name: 'protective_equipment_required',
          title: 'Protective Equipment Required',
          type: 'array',
          of: [{ type: 'string' }],
        }),
      ],
      group: 'technical'
    }),

    // SEO & CONTENT TAB
    defineField({
      name: 'keywords',
      title: 'Keywords',
      type: 'array',
      of: [{ type: 'string' }],
      group: 'seo'
    }),
    defineField({
      name: 'related_products',
      title: 'Related Products',
      type: 'array',
      of: [{ type: 'reference', to: [{ type: 'equipment' }] }],
      group: 'seo'
    }),

    // AI GENERATED TAB
    defineField({
      name: 'ai_suggested_use_cases',
      title: 'AI Suggested Use Cases',
      type: 'array',
      of: [{ type: 'string' }],
      group: 'ai'
    }),
    defineField({
      name: 'ai_keywords',
      title: 'AI Keywords',
      type: 'array',
      of: [{ type: 'string' }],
      group: 'ai'
    }),
    defineField({
      name: 'ai_project_types',
      title: 'AI Project Types',
      type: 'array',
      of: [{ type: 'string' }],
      group: 'ai'
    }),

    // METADATA & REVIEWS TAB
    defineField({
      name: 'created_date',
      title: 'Created Date',
      type: 'datetime',
      group: 'metadata'
    }),
    defineField({
      name: 'last_updated',
      title: 'Last Updated',
      type: 'datetime',
      group: 'metadata'
    }),
    defineField({
      name: 'popularity_score',
      title: 'Popularity Score',
      type: 'number',
      group: 'metadata'
    }),
  ],
  preview: {
    select: {
      title: 'name',
      subtitle: 'id',
      categories: 'categories',
    },
    prepare(selection) {
      const { title, subtitle, categories } = selection;
      return {
        title,
        subtitle: subtitle + (categories && categories.length > 0 ? ` • ${categories[0]}` : ''),
      };
    },
  },
});