
import { defineField, defineType } from 'sanity';

export default defineType({
  name: 'equipment',
  title: 'Equipment',
  type: 'document',
  fields: [
    defineField({
      name: 'id',
      title: 'ID',
      type: 'string',
      validation: (Rule) => Rule.required(),
    }),
    defineField({
      name: 'sku',
      title: 'SKU',
      type: 'string',
    }),
    defineField({
      name: 'name',
      title: 'Name',
      type: 'string',
      validation: (Rule) => Rule.required(),
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
    }),
    defineField({
      name: 'categories',
      title: 'Categories',
      type: 'array',
      of: [{ type: 'string' }],
    }),
    defineField({
      name: 'subcategories',
      title: 'Subcategories',
      type: 'array',
      of: [{ type: 'string' }],
    }),
    defineField({
      name: 'short_description',
      title: 'Short Description',
      type: 'text',
      rows: 2,
    }),
    defineField({
      name: 'full_description',
      title: 'Full Description',
      type: 'text',
    }),
    defineField({
      name: 'technical_description',
      title: 'Technical Description',
      type: 'text',
    }),
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
    }),
    defineField({
      name: 'video_urls',
      title: 'Video URLs',
      type: 'array',
      of: [{ type: 'url' }],
    }),
    defineField({
      name: 'manual_urls',
      title: 'Manual URLs',
      type: 'array',
      of: [{ type: 'url' }],
    }),
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
    }),
    defineField({
      name: 'dimensions',
      title: 'Dimensions',
      type: 'object',
      fields: [
        defineField({
          name: 'length',
          title: 'Length',
          type: 'number',
        }),
        defineField({
          name: 'width',
          title: 'Width',
          type: 'number',
        }),
        defineField({
          name: 'height',
          title: 'Height',
          type: 'number',
        }),
        defineField({
          name: 'unit',
          title: 'Unit',
          type: 'string',
        }),
      ],
    }),
    defineField({
      name: 'power_source',
      title: 'Power Source',
      type: 'string',
    }),
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
        defineField({
          name: 'next_available_date',
          title: 'Next Available Date',
          type: 'datetime',
        }),
        defineField({
          name: 'maintenance_schedule',
          title: 'Maintenance Schedule',
          type: 'text',
        }),
      ],
    }),
    defineField({
      name: 'primary_use_cases',
      title: 'Primary Use Cases',
      type: 'array',
      of: [{ type: 'string' }],
    }),
    defineField({
      name: 'secondary_use_cases',
      title: 'Secondary Use Cases',
      type: 'array',
      of: [{ type: 'string' }],
    }),
    defineField({
      name: 'industries_served',
      title: 'Industries Served',
      type: 'array',
      of: [{ type: 'string' }],
    }),
    defineField({
      name: 'project_types',
      title: 'Project Types',
      type: 'array',
      of: [{ type: 'string' }],
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
        defineField({
          name: 'compliance_standards',
          title: 'Compliance Standards',
          type: 'array',
          of: [{ type: 'string' }],
        }),
        defineField({
          name: 'age_restrictions',
          title: 'Age Restrictions',
          type: 'number',
        }),
      ],
    }),
    defineField({
      name: 'keywords',
      title: 'Keywords',
      type: 'array',
      of: [{ type: 'string' }],
    }),
    defineField({
      name: 'search_tags',
      title: 'Search Tags',
      type: 'array',
      of: [{ type: 'string' }],
    }),
    defineField({
      name: 'related_products',
      title: 'Related Products',
      type: 'array',
      of: [{ type: 'reference', to: [{ type: 'equipment' }] }],
    }),
    defineField({
      name: 'created_date',
      title: 'Created Date',
      type: 'datetime',
    }),
    defineField({
      name: 'last_updated',
      title: 'Last Updated',
      type: 'datetime',
    }),
    defineField({
      name: 'review_count',
      title: 'Review Count',
      type: 'number',
    }),
    defineField({
      name: 'brand',
      title: 'Brand',
      type: 'string',
    }),
    defineField({
      name: 'model',
      title: 'Model',
      type: 'string',
    }),
    defineField({
      name: 'weight',
      title: 'Weight',
      type: 'number',
    }),
    defineField({
      name: 'popularity_score',
      title: 'Popularity Score',
      type: 'number',
    }),
    defineField({
      name: 'review_rating',
      title: 'Review Rating',
      type: 'number',
    }),
    defineField({
      name: 'ai_suggested_use_cases',
      title: 'AI Suggested Use Cases',
      type: 'array',
      of: [{ type: 'string' }],
    }),
    defineField({
      name: 'ai_keywords',
      title: 'AI Keywords',
      type: 'array',
      of: [{ type: 'string' }],
    }),
    defineField({
      name: 'ai_project_types',
      title: 'AI Project Types',
      type: 'array',
      of: [{ type: 'string' }],
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
