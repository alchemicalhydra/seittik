import fs from 'fs'

import * as babelCore from '@babel/core'
import webpack from 'webpack'
import TerserPlugin from 'terser-webpack-plugin'


const babelOptions = babelCore.loadOptions()


for (const i in babelOptions.presets) {
  const preset = babelOptions.presets[i]
  if (preset === 'env') {
    babelOptions.presets[i] = ['env', {
      modules: false,
    }]
  }
}


export default function (env, argv) {
  return {
    mode: 'production',
    entry: './_src/index.js',
    module: {
      rules: [
        {
          test: /\.m?js$/,
          exclude: /\/node_modules\//,
          use: [
            {
              loader: 'babel-loader',
              options: babelOptions,
            },
          ],
        },
      ],
    },
    optimization: {
      minimize: true,
      minimizer: [
        new TerserPlugin({
          extractComments: false,
          terserOptions: {
            output: {
              comments: false,
            },
          },
        }),
      ],
    },
    output: {
      filename: './_static/js/index.js',
      path: __dirname,
    },
    plugins: [
    ],
  }
}
